from .api_connection import url_conn, get_competitions, get_fixtures, \
    get_team_last_fixtures, get_league_table
from .models import AppUser, User, Competition, Fixture, Team, Bet

from django.core.exceptions import ObjectDoesNotExist

from random import randint
#  Bundesliga 1
ID = 430
# season 2016


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


def get_team_balance(league_table, team_name, venue):
    """
    Gets team balance from league table
    :param league_table: json object of league table
    :param team_name: string
    :param venue: string - home/away
    :return: dict - with int values of wins, draws, losses
    """

    # iterate through list and find selected team
    for team in league_table['standing']:
        if team['teamName'] == team_name:
            wins = team[venue]['wins']
            draws = team[venue]['draws']
            losses = team[venue]['losses']

            # if there is no matches in league table then wins/draws/losses
            # TODO: make it more probable
            if wins == 0 and draws == 0 and losses == 0:
                wins = randint(1, 10)
                draws = randint(1, 10)
                losses = randint(1, 10)

            balance = {"wins": wins,
                       "draws": draws,
                       "losses": losses
                       }
            return balance


def calculate_result_odds(balance):
    """
    Calculates result odd based on home team  home wins/draws/losses and
    away team away wins/draws/losses
    :param balance: dict - dict with int's of hme/away wins/draws/losses
    :return: dict - of float numbers of home win/draw/away win
    """

    home_wins = balance['home_wins']
    home_draws = balance['home_draws']
    home_losses = balance['home_losses']
    away_wins = balance['away_wins']
    away_draws = balance['away_draws']
    away_losses = balance['away_losses']
    # sums all games
    sum_of_fixtures = sum([home_wins, home_draws, home_losses, away_wins,
                           away_draws, away_losses])

    # calculates prices of particular outcomes
    # not great algorithm of calculating odds but for this app it will suffice
    home_price = home_wins + away_losses
    draw_price = home_draws + away_draws
    away_price = home_losses + away_wins

    home_win = round(1 / (home_price / sum_of_fixtures), 2)
    draw = round(1 / (draw_price / sum_of_fixtures), 2)
    away_win = round(1 / (away_price / sum_of_fixtures), 2)

    odds = {'home_win': home_win,
            'draw': draw,
            'away_win': away_win
            }

    return odds


def calculate_odds(home_team_name,
                   away_team_name,
                   league_table
                   ):
    """
    This is not a good way of calculating odds but for needs of this simple 
    app it will suffice. 
    :param home_team_name: string 
    :param away_team_name: string
    :return: calculated odds of home_win, draw, away_win
    """

    home_team_balance = get_team_balance(league_table,
                                         home_team_name,
                                         'home'
                                         )

    away_team_balance = get_team_balance(league_table,
                                         away_team_name,
                                         'away'
                                         )

    both_teams_balance = {'home_wins': home_team_balance['wins'],
                          'home_draws': home_team_balance['draws'],
                          'home_losses': home_team_balance['losses'],
                          'away_wins': away_team_balance['wins'],
                          'away_draws': away_team_balance['draws'],
                          'away_losses': away_team_balance['losses'],
                          }

    return calculate_result_odds(both_teams_balance)


def create_fixture(home_team_name, away_team_name, matchday, date, competition,
                   away_win, draw, home_win):
    """
    Creates fixture and saves it to db
    :param home_team_name: string
    :param away_team_name: string
    :param matchday: int
    :param date: string
    :param competition: Competition object
    :param away_win: float - odds of away win
    :param draw: float - odds of draw
    :param home_win: float - odds of home win
    :return: 
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
                               date=date,
                               course_team_home_win=home_win,
                               course_team_away_win=away_win,
                               course_draw=draw
                               )


def create_fixtures(link_fixtures, competition, league_table):
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
        matchday = fixture_data['matchday']
        date = fixture_data['date']
        odds = calculate_odds(home_team, away_team, league_table)

        home_win = odds['home_win']
        draw = odds['draw']
        away_win = odds['away_win']

        create_fixture(home_team, away_team, matchday, date, competition,
                       away_win, draw, home_win)


def create_competition(competition_id=ID):
    """
    Gets data from competiton json, creates Competition object if doesnt already 
    exist and saves it to db, runst functions that create teams and fixtures 
    related with this competition
    :param competition_id: int - id of competition in api server
    :param season: int - year of season start
    """
    data = get_competitions(id=competition_id)
    caption = data['caption']
    league = data['league']
    number_of_matchdays = data['numberOfMatchdays']
    year = data['year']
    number_of_teams = data['numberOfTeams']
    current_matchday = data["currentMatchday"]

    # get league table link
    league_table_link = data['_links']['leagueTable']['href']
    # get league table
    league_table = url_conn(league_table_link)

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
    create_fixtures(link_fixtures, comp, league_table)


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
        else:
            bet.bet_result = 0
            bet.save()


def update_fixture(fixture, goals_away_team, goals_home_team):
    """
    Updates given fixture with away/home goals and runs function that
    checks all bets related to fixture
    :param fixture: Fixture object
    :param goals_away_team: int
    :param goals_home_team: int
    :return: None
    """
    # if fixture status == SCHEDULED or PLAYING update fixture, save it and run
    # function that checks related bets
    if fixture.status == 1 or fixture.status == 3:
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


def update_fixtures(competition_id=ID, matchday=""):
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
    # picks needed competition data
    for data_row in fixtures_data:
        date = data_row['date']
        away_team_name = data_row['awayTeamName']
        home_team_name = data_row['homeTeamName']
        matchday = data_row['matchday']
        goals_away_team = data_row['result']['goalsAwayTeam']
        goals_home_team = data_row['result']['goalsHomeTeam']
        # fixture_status = data_row['status']

        fixture = get_fixture(date,
                              away_team_name,
                              home_team_name,
                              matchday,
                              competition
                              )
        if fixture.get_status_display() != "FINISHED":
            update_fixture(fixture, goals_away_team, goals_home_team)
    # updates odds in fixtures after each fixtures update
    update_odds_in_fixtures(competition_id)


def update_odds_in_fixtures(competition_id):
    """
    Updates odds for scheduled fixtures
    :param competition_id: int
    :return: None
    """
    league_table = get_league_table(competition_id)

    fixtures = Fixture.objects.filter(status=1)

    for fixture in fixtures:
        home_team_name = fixture.home_team.name
        away_team_name = fixture.away_team.name
        odds = calculate_odds(home_team_name, away_team_name, league_table)
        fixture.course_team_home_win = odds['home_win']
        fixture.course_draw = odds['draw']
        fixture.course_team_away_win = odds['away_win']
        fixture.save()


"from betapp.update_db import *"
"create_competition()"
'update_fixtures(matchday=1)'
