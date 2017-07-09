from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin, \
    PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy

from .models import *
from .forms import *
from .api_connection import get_competitions


class CompetitionsView(View):
    def get(self, request):
        """
        Displays all competitions in db
        :return: rendered html with all competitions
        """
        competitions = Competition.objects.all()
        context = {"competitions": competitions}
        return render(request, 'competitions.html', context)


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
    login_url = reverse_lazy('login')

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
                Bet.objects.create(bet_user=app_user,
                                   bet_amount=bet_amount,
                                   fixture=fixture,
                                   bet=bet,
                                   bet_course=bet_course
                                   )
        return redirect(reverse_lazy('competitions'))


class LoginView(UserPassesTestMixin, FormView):
    def test_func(self):
        # tests if user is authenticated
        return not self.request.user.is_authenticated
    template_name = "login_form.html"
    form_class = LoginForm
    success_url = reverse_lazy('competitions')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self, username=username, password=password)
        if user is not None:
            login(self.request, user)
        else:
            messages = ["Wrong username or password"]
            form = LoginForm()
            context = {"messages": messages,
                       "form": form
                       }
            return render(self.request, "login_form.html", context)
        return super(LoginView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('competitions'))


def check_if_exists(username):
    return User.objects.filter(username=username).exists()


class RegisterView(FormView):
    def test_func(self):
        return not self.request.user.is_authenticated

    template_name = "register_form.html"
    form_class = RegisterForm
    success_url = reverse_lazy('competitions')

    def form_valid(self, form):
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
    login_url = reverse_lazy('login')

    def get(self, request):
        user = request.user
        app_user = AppUser.objects.get(user=user)
        bets = Bet.objects.filter(bet_user=app_user)
        context = {"user": user,
                   "app_user": app_user,
                   "bets": bets,
                   }
        return render(request, "my_account.html", context)


class ShowTeamView(View):
    def get(self, request, team_id):
        team = Team.objects.get(id=team_id)
        competition = team.competition
        team_fixtures_home = Fixture.objects.filter(home_team=team)
        team_fixtures_away = Fixture.objects.filter(away_team=team)

        all_fixtures = [game for game in team_fixtures_away] + [game for game in team_fixtures_home]

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
        competitions = get_competitions(season=season)

        context = {"competitions": competitions}
        return render(request, 'list_competitions.html', context)

    def post(self, request, season):
        selected_copmetitions = request.POST.getlist('competition')
        print(selected_copmetitions)
        return redirect(reverse_lazy('competitions'))

