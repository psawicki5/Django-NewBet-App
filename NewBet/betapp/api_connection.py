import requests

url ='http://api.football-data.org/v1/competitions/445'
url_teams = "http://api.football-data.org/v1/competitions/445/teams"
url_players = "http://api.football-data.org/v1/teams/57/players"
url_team = "http://api.football-data.org/v1/teams/57"
url_fixtures_for_team = "http://api.football-data.org/v1/teams/57/fixtures/"
url_league_table =  "http://api.football-data.org/v1/competitions/445/leagueTable"


def url_conn(url):
    api_key = "42a9d88dc690467b91d18285e9d6c9a8"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, verify=True, headers=headers)
    if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit()
    return response.json()


def get_competitions(id="", season=""):
    url = 'http://api.football-data.org/v1/' \
          'competitions/{}?season={}'.format(id, season)
    return url_conn(url)


def get_fixtures(competition_id, matchday):
    url = 'http://api.football-data.org/v1/' \
          'competitions/{}/fixtures?matchday={}'.format(competition_id,
                                                        matchday
                                                        )
    return url_conn(url)

#print(get_fixtures(394, 1))










