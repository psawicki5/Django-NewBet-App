from .api_connection import url_conn, get_competitions, get_fixtures
from .models import AppUser, User, Competition, Fixture, Team, Bet

from django.core.exceptions import ObjectDoesNotExist

#  Bundesliga 1
ID = 394
# season 2015
SEASON = 2015


def create_team(name, crest_url, code, short_name, competition):
    try:
        Team.objects.get(name=name, competition=competition)
    except ObjectDoesNotExist:
        Team.objects.create(name=name,
                            crest_url=crest_url,
                            code=code,
                            short_name=short_name,
                            competition=competition
                            )


def create_teams(link_teams, competition):
    data = url_conn(link_teams)['teams']
    for team_data in data:
        name = team_data['name']
        crest_url = team_data['crestUrl']
        code = team_data['code']
        short_name = team_data['shortName']

        create_team(name, crest_url, code, short_name, competition)


def clear_date(date):
    date = date.replace("T", " ")
    date = date.replace("Z", "")
    return date


def create_fixture(home_team_name, away_team_name, matchday, date, competition):
    home_team = Team.objects.get(name=home_team_name, competition=competition)
    away_team = Team.objects.get(name=away_team_name, competition=competition)

    try:
        fixture = Fixture.objects.get(home_team=home_team,
                                      away_team=away_team,
                                      competition=competition,
                                      matchday=matchday,
                                      )
    except ObjectDoesNotExist:
        Fixture.objects.create(home_team=home_team,
                               away_team=away_team,
                               competition=competition,
                               matchday=matchday,
                               date=date
                               )


def create_fixtures(link_fixtures, competition):
    data = url_conn(link_fixtures)['fixtures']
    for fixture_data in data:
        home_team = fixture_data['homeTeamName']
        away_team = fixture_data['awayTeamName']
        matchday = fixture_data['matchday']
        date = fixture_data['date']

        create_fixture(home_team, away_team, matchday, date, competition)


def create_competition():
    data = get_competitions(id=ID, season=SEASON)
    caption = data['caption']
    league = data['league']
    number_of_matchdays = data['numberOfMatchdays']
    year = data['year']
    number_of_teams = data['numberOfTeams']
    current_matchday = data["currentMatchday"]

    try:
        comp = Competition.objects.get(caption=caption, year=year)
    except ObjectDoesNotExist:
        comp = Competition(caption=caption,
                           league=league,
                           number_of_matchdays=number_of_matchdays,
                           year=year,
                           number_of_teams=number_of_teams,
                           current_matchday=current_matchday
                           )
        comp.save()
    link_teams = data['_links']['teams']['href']
    link_fixtures = data['_links']['fixtures']['href']
    create_teams(link_teams, comp)
    create_fixtures(link_fixtures, comp)


def get_team(name, competition):
    return Team.objects.get(name=name, competition=competition)


def get_fixture(date, away_team_name, home_team_name, matchday, competition):
    away_team = get_team(away_team_name, competition)
    home_team = get_team(home_team_name, competition)
    return Fixture.objects.get(home_team=home_team,
                               away_team=away_team,
                               date=date,
                               matchday=matchday,
                               competition=competition
                               )


def get_fixture_result(goals_home_team, goals_away_team):
    if goals_home_team > goals_away_team:
        return 1
    elif goals_home_team == goals_away_team:
        return 0
    elif goals_home_team < goals_away_team:
        return 2


def cash_user(bet):
    app_user = bet.bet_user
    if bet.bet_result == 1:
        cash_win = bet.bet_amount * bet.bet_course
        app_user.cash += cash_win
        app_user.save()


def check_bets(fixture):
    bets = Bet.objects.filter(fixture=fixture)

    for bet in bets:
        if bet.bet == fixture.fixture_result:
            bet.bet_result = 1
            bet.save()
            cash_user(bet)


def update_fixture(fixture, goals_away_team, goals_home_team):
    if fixture.status == 1:
        'and not fixture.goals_away_team and not fixture.goals_home_team)'
        fixture.goals_home_team = goals_home_team
        fixture.goals_away_team = goals_away_team
        fixture.status = 2  # fixture PLAYED
        #  Get fixture bet result 1, 2 or 0
        fixture.fixture_result = get_fixture_result(goals_home_team,
                                                    goals_away_team
                                                    )
        fixture.save()
        check_bets(fixture)


def update_fixtures(competition_id=ID, matchday=1):
    data = get_fixtures(competition_id, matchday)
    fixtures_data = data['fixtures']

    competition_data = get_competitions(id=competition_id)
    competition_caption = competition_data['caption']
    competition_year = competition_data['year']

    competition = Competition.objects.get(caption=competition_caption,
                                          year=competition_year
                                          )

    for data_row in fixtures_data:
        date = data_row['date']
        away_team_name = data_row['awayTeamName']
        home_team_name = data_row['homeTeamName']
        matchday = data_row['matchday']
        goals_away_team = data_row['result']['goalsAwayTeam']
        goals_home_team = data_row['result']['goalsHomeTeam']

        fixture = get_fixture(date,
                              away_team_name,
                              home_team_name,
                              matchday,
                              competition
                              )
        update_fixture(fixture, goals_away_team, goals_home_team)


"from betapp.update_db import *"
"create_competition()"
'update_fixtures(matchday=1)'