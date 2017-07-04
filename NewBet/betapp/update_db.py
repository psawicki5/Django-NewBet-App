from .api_connection import *
from .models import *

from django.core.exceptions import ObjectDoesNotExist


def create_team(name, crestUrl, code, shortName, competition):
    try:
        Team.objects.get(name=name, competition=competition)
    except ObjectDoesNotExist:
        Team.objects.create(name=name,
                            crestUrl=crestUrl,
                            code=code,
                            shortName=shortName,
                            competition=competition
                            )


def create_teams(link_teams, competition):
    data = url_conn(link_teams)['teams']
    for team_data in data:
        name = team_data['name']
        crestUrl = team_data['crestUrl']
        code = team_data['code']
        shortName = team_data['shortName']

        create_team(name, crestUrl, code, shortName, competition)


def clear_date(date):
    date = date.replace("T", " ")
    date = date.replace("Z", "")
    return date


def create_fixture(homeTeamName, awayTeamName, matchday, date, competition):
    homeTeam = Team.objects.get(name=homeTeamName, competition=competition)
    awayTeam = Team.objects.get(name=awayTeamName, competition=competition)

    try:
        fixture = Fixture.objects.get(homeTeam=homeTeam,
                                      awayTeam=awayTeam,
                                      competition=competition,
                                      matchday=matchday,
                                     )
    except ObjectDoesNotExist:
        Fixture.objects.create(homeTeam=homeTeam,
                               awayTeam=awayTeam,
                               competition=competition,
                               matchday=matchday,
                               date=date
                               )


def create_fixtres(link_fixtures, competition):
    data = url_conn(link_fixtures)['fixtures']
    for fixture_data in data:
        homeTeam = fixture_data['homeTeamName']
        awayTeam = fixture_data['awayTeamName']
        matchday = fixture_data['matchday']
        #date = clear_date(fixture_data['date'])
        date = fixture_data['date']

        create_fixture(homeTeam, awayTeam, matchday, date, competition)


def create_competition():
    data = get_competitions(id=394, season=2015)
    caption = data['caption']
    league = data['league']
    numberOfMatchdays = data['numberOfMatchdays']
    year = data['year']
    numberOfTeams = data['numberOfTeams']
    currentMatchday = data["currentMatchday"]

    try:
        comp = Competition.objects.get(caption=caption, year=year)
    except ObjectDoesNotExist:
        comp = Competition(caption=caption,
                           league=league,
                           numberOfMatchdays=numberOfMatchdays,
                           year=year,
                           numberOfTeams=numberOfTeams,
                           currentMatchday=currentMatchday
                           )
        comp.save()
    link_teams = data['_links']['teams']['href']
    link_fixtures = data['_links']['fixtures']['href']
    create_teams(link_teams, comp)
    create_fixtres(link_fixtures, comp)


"from betapp.update_db import *"
"create_competition()"