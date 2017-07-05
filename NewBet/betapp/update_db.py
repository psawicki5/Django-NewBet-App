from .api_connection import *
from .models import *

from django.core.exceptions import ObjectDoesNotExist


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
    data = get_competitions(id=394, season=2015)
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


"from betapp.update_db import *"
"create_competition()"