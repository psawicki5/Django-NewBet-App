import requests

api_key = "42a9d88dc690467b91d18285e9d6c9a8"

url ='http://api.football-data.org/v1/competitions/445'
url_teams = "http://api.football-data.org/v1/competitions/445/teams"
url_players = "http://api.football-data.org/v1/teams/{id}/players"
url_team = "http://api.football-data.org/v1/teams/57"

headers = {'X-Auth-Token': api_key}
response = requests.get(url, verify=True, headers=headers)
if response.status_code != 200:
    print('Status:', response.status_code, 'Problem with the request. Exiting.')

data = response.json()
print(data)

for row in data:
    print(row)
