from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin, \
    LoginRequiredMixin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

import redis

from .models import *
from .forms import *
from .api_connection import get_competitions, get_league_table
from .update_db import create_competition
from .tasks import bet_created


r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB,
                      decode_responses=True)


class CompetitionsView(ListView):
    """
    Displays all competitions
    """
    model = Competition
    template_name = "competitions.html"


class CompetitionView(View):
    def get(self, request, id):
        """
        Displays competition and all fixtures in competition
        :param request: 
        :param id: int - competition id in db
        :return: rendered html with competition and fixtures
        """
        competition = Competition.objects.get(id=id)
        fixtures = Fixture.objects.filter(competition=competition,
                                          status=1,
                                          )
        context = {"competition": competition,
                   "fixtures": fixtures
                   }
        return render(request, 'fixtures.html', context)


class CompetitionTableView(View):
    def get(self, request, id):
        competition = Competition.objects.get(id=id)
        api_id = competition.api_id
        league_table = get_league_table(api_id)
        table = []
        for team in league_table['standing']:
            table.append({"position": team['position'],
                          "name": team['teamName'],
                          "games": team['playedGames'],
                          "wins": team['wins'],
                          "draws": team['draws'],
                          "losses": team['losses'],
                          "points": team['points'],
                          })
        context = {"table": table, "competition": competition}
        return render(request, 'league_table.html', context)


def get_bet_course(fixture, bet):
    """
    Gets bet course from fixture and returns it
    :param fixture: Fixture object
    :param bet: int - 1:home_win, 2:away_win, 0:draw
    :return: float - course
    """
    if bet == 1:
        return fixture.course_team_home_win
    elif bet == 0:
        return fixture.course_draw
    elif bet == 2:
        return fixture.course_team_away_win


class BetFixtureView(LoginRequiredMixin, View):
    redirect_field_name = "next"

    def get(self, request, id):
        """
        Displays form for betting 
        :param id: int - id of fixture
        :return: rendered form
        """
        fixture = Fixture.objects.get(id=id)
        if fixture.status == 1:
            form = BetForm
            context = {"fixture": fixture,
                       "form": form
                       }
            return render(request, "bet_form.html", context)

    def post(self, request, id):
        """
        Checks if form is valid, user has the cash, cash amount is valid and 
        then saves bet ot db
        :param id: int - fixture id
        :return: redirection to competitions view
        """
        fixture = Fixture.objects.get(id=id)
        user = request.user
        app_user = AppUser.objects.get(user=user)
        form = BetForm(request.POST)
        if form.is_valid():
            bet_amount = form.cleaned_data['bet_amount']
            bet = form.cleaned_data['bet']
            bet_course = get_bet_course(fixture, bet)
            # check if cash amount is valid
            if app_user.cash - bet_amount >= 0 and bet_amount >= 0.01:
                app_user.cash -= bet_amount
                app_user.save()
                bet = Bet.objects.create(bet_user=app_user,
                                         bet_amount=bet_amount,
                                         fixture=fixture,
                                         bet=bet,
                                         bet_course=bet_course
                                         )
                bet_created.delay(bet.id)
        return redirect(reverse_lazy('competitions'))


def check_if_exists(username):
    """
    Checks if user exists in db
    :param username: string
    :return: Not empty queryset if user in db else returns empty queryset
    """
    return User.objects.filter(username=username).exists()


class RegisterView(FormView):
    def test_func(self):
        return not self.request.user.is_authenticated

    template_name = "register_form.html"
    form_class = RegisterForm
    success_url = reverse_lazy('competitions')

    def form_valid(self, form):
        """
        Adds new AppUser to db
        :param form: form object
        :return: redirect to competitions view
        """
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']

        messages = []
        flag = True

        if check_if_exists(username):
            messages.append("User already exists!!")
            flag = False
        if password != confirm_password:
            messages.append("Passwords dont match!!")
            flag = False

        if flag:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            email=email
                                            )
            AppUser.objects.create(user=user,
                                   bank_account_number=111,
                                   cash=100
                                   )
        else:
            form = RegisterForm()
            context = {"messages": messages,
                       "form": form
                       }
            return render(self.request, "register_form.html", context)
        return super(RegisterView, self).form_valid(form)


class AccountDetailsView(LoginRequiredMixin, View):
    redirect_field_name = 'next'

    def get(self, request):
        """
        Displays AppUser's account details
        :return: html with account details
        """
        user = request.user
        app_user = AppUser.objects.get(user=user)
        bets = Bet.objects.filter(bet_user=app_user)
        context = {"user": user,
                   "app_user": app_user,
                   "bets": bets,
                   }
        return render(request, "my_account.html", context)


class TeamStandingsView(APIView):
    def get(self, request, competition_id, team_id):
        print(competition_id, team_id)
        list_name = "{}:{}:standing".format(competition_id, team_id)
        standings = r.hgetall(list_name)
        matchday_list = sorted([int(i) for i in standings.keys()])
        standing_list = [int(standings[str(mday)])for mday in matchday_list]
        data = {"matchday_list": matchday_list,
                "standing_list": standing_list
                }
        return Response(data)



class ShowTeamView(View):
    def get(self, request, team_id):
        """
        Displays Team object's details 
        :param team_id: int - id of Team object in db
        :return: html with team details
        """
        team = Team.objects.get(id=team_id)
        competition = team.competition
        team_fixtures_home = Fixture.objects.filter(home_team=team)
        team_fixtures_away = Fixture.objects.filter(away_team=team)

        all_fixtures = [game for game in team_fixtures_away] +\
                       [game for game in team_fixtures_home]

        played_fixtures = [game for game in all_fixtures if game.status == 2]
        scheduled_fixtures = [game for game in all_fixtures if game.status == 1]

        context = {"team": team,
                   "competition": competition,
                   "team_fixtures_home": team_fixtures_home,
                   "team_fixtures_away": team_fixtures_away,
                   "played_fixtures": played_fixtures,
                   "scheduled_fixtures": scheduled_fixtures
                   }

        return render(request, "show_team.html", context)


class AddCompetitionsView(PermissionRequiredMixin, View):
    permission_required = ['is_superuser']

    def get(self, request, season):
        """
        Displays all available teams for season and anables to select them 
        to be added to db. 
        Competitions can be added only by superuser!!!
        :param season: int - season start year
        :return: renders html with checkboxes for competition selection
        """
        competitions = get_competitions(season=season)

        context = {"competitions": competitions}
        return render(request, 'list_competitions.html', context)

    def post(self, request, season):
        """
        Adds selected competitions to db
        :param season: int - season start year
        :return: redirection to competitions view
        """
        selected_copmetitions = request.POST.getlist('competition')
        for competition_id in selected_copmetitions:
            create_competition(int(competition_id))
        return redirect(reverse_lazy('competitions'))


class FinishedFixturesView(View):
    def get(self, request, id):
        competition = Competition.objects.get(id=id)
        finished_fixtures = Fixture.objects.filter(competition=competition,
                                                 status=2)
        context = {"competition": competition,
                   "finished_fixtures": finished_fixtures
                   }
        return render(request, 'finished_fixtures.html', context)
