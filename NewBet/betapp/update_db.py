from .api_connection import url_conn, get_competitions, get_fixtures, \
    get_team_last_fixtures
from .models import AppUser, User, Competition, Fixture, Team, Bet

from django.core.exceptions import ObjectDoesNotExist

import re

#  Bundesliga 1
ID = 394
# season 2015
SEASON = 2015


def create_team(name, crest_url, code, short_name, competition):
    """
    Creates single Team object and saves it to db
    :param name: string - name of team
    :param crest_url: string - url to crest of team
    :param code: string - codename of team
    :param short_name: string - shortened name of team
    :param competition: Competition object
    """
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
    """
    Iterates through team data recieved from json from link_teams,
    retrievs team data, then runs function that creates 
    function that creates Team objects
    :param link_teams: string - link to teams data json
    :param competition: Competition object that teams contribute to
    """
    data = url_conn(link_teams)['teams']
    for team_data in data:
        name = team_data['name']
        crest_url = team_data['crestUrl']
        code = team_data['code']
        short_name = team_data['shortName']

        create_team(name, crest_url, code, short_name, competition)


def get_team_balance(team_last_fixtures, team_name):
    wins = 0
    draws = 0
    losses = 0
    # TODO: Finish this function


def calculate_odds(home_team_api_id, away_team_api_id, home_team_name, away_team_name):
    home_team_last_fixtures = get_team_last_fixtures(home_team_api_id)
    away_team_last_fixtures = get_team_last_fixtures(away_team_api_id)
    # TODO: Finish this function


def create_fixture(home_team_name, away_team_name, matchday, date, competition):
    """
    Creates Fixture object and saves it ot db
    :param home_team_name: string
    :param away_team_name: string
    :param matchday: int
    :param date: string - date of fixture
    :param competition: Competition object that fixtures contribute to
    """
    #  Get Team objects
    home_team = Team.objects.get(name=home_team_name, competition=competition)
    away_team = Team.objects.get(name=away_team_name, competition=competition)

    # Try to get fixture if exist, else create new fixture object
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


def separate_id(href):
    """
    Separates team_api_id from link
    :param href: string - link to team data
    :return: int id of team in api server
    """
    team_api_id = re.findall('/([\d]+)', href)
    team_api_id = int(team_api_id[0])
    return team_api_id


def create_fixtures(link_fixtures, competition):
    """
    Iterates through team data recieved from link_fixtures json,
    retrieves data from json and runs function that create Fixture objects
    :param link_fixtures: string - link to json fixture data
    :param competition: Competition object
    """
    data = url_conn(link_fixtures)['fixtures']
    for fixture_data in data:
        home_team = fixture_data['homeTeamName']
        away_team = fixture_data['awayTeamName']
        away_tema_api_id = separate_id(fixture_data['awayTeam']['href'])
        home_tema_api_id = separate_id(fixture_data['homeTeam']['href'])
        matchday = fixture_data['matchday']
        date = fixture_data['date']
################################################################################
        #calculate_odds(home_team_api_id, away_team_api_id , home_team.name, away_team.name)

        create_fixture(home_team, away_team, matchday, date, competition)


def create_competition(competition_id=ID, season=SEASON):
    """
    Gets data from competiton json, creates Competition object if doesnt already 
    exist and saves it to db, runst functions that create teams and fixtures 
    related with this competition
    :param competition_id: int - id of competition in api server
    :param season: int - year of season start
    """
    data = get_competitions(id=competition_id, season=season)
    caption = data['caption']
    league = data['league']
    number_of_matchdays = data['numberOfMatchdays']
    year = data['year']
    number_of_teams = data['numberOfTeams']
    current_matchday = data["currentMatchday"]

    # Try to get competition object of given caption and year, if doesnt exist
    # create new Competition
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
    """
    Gets Team object from db based on team name and competition
    :param name: string - team name
    :param competition: Competition object
    :return: Team object
    """
    return Team.objects.get(name=name, competition=competition)


def get_fixture(date, away_team_name, home_team_name, matchday, competition):
    """
    Gets Fixture objects and returns it
    :param date: string - date of fixture
    :param away_team_name: string 
    :param home_team_name: string
    :param matchday: int
    :param competition: Competition object
    :return: Fixture object
    """

    # retrievs Team objects from db
    away_team = get_team(away_team_name, competition)
    home_team = get_team(home_team_name, competition)
    return Fixture.objects.get(home_team=home_team,
                               away_team=away_team,
                               date=date,
                               matchday=matchday,
                               competition=competition
                               )


def get_fixture_result(goals_home_team, goals_away_team):
    """
    Returns fixture result based on home/away goals
    :param goals_home_team: int
    :param goals_away_team: int
    :return: if home win: 1, else if draw: 0, else if away win: 2
    """
    if goals_home_team > goals_away_team:
        return 1
    elif goals_home_team == goals_away_team:
        return 0
    elif goals_home_team < goals_away_team:
        return 2


def cash_user(bet):
    """
    Transfers money to AppUser account if user had won his bet
    :param bet: Bet object
    """
    app_user = bet.bet_user
    # if bet result == 1(winning bet) transfer money to user account
    # this condition is checked just in case...
    if bet.bet_result == 1:
        cash_win = bet.bet_amount * bet.bet_course
        app_user.cash += cash_win
        app_user.save()


def check_bets(fixture):
    """
    Checks all bets related to given fixture
    :param fixture: Fixture object
    """
    bets = Bet.objects.filter(fixture=fixture)

    for bet in bets:
        # if bet(possibilities: 1, 0, 2) is
        # the same as fixture result(possibilities: 1, 0, 2),
        # set bet result to 1(winning bet) and run function that transfer cash
        if bet.bet == fixture.fixture_result:
            bet.bet_result = 1
            bet.save()
            cash_user(bet)


def update_fixture(fixture, goals_away_team, goals_home_team):
    """
    Updates given fixture with away/home goals and runs function that
    checks all bets related to fixture
    :param fixture: Fixture object
    :param goals_away_team: int
    :param goals_home_team: int
    :return: None
    """
    # if fixture status == SCHEDULED update fixture, save it and run function
    # that checks related bets
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
    """
    Updates fixtures with data from api server. 
    Fixtures are updated according to matchday.
    :param competition_id: int - id of competition in api server
    :param matchday: int - number of matchday
    :return: None
    """
    # gets data from api serer
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