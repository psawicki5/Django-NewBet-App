## NewBetApp
  
Betting aplication based on Django.   
Application uses the http://www.football-data.org API server for football data.  
API provides competitions, teams, fixtures, teams etc.  
Program allows user to bet fixtures. User can bet home win, draw or away win. 
Program schedules fixtures, automatically checks if fixture have started/finished and  
calculates bet payout (if bet has benn won). Application also calculates odds of fixtures   
based on current league table. Odds are recalculated after each matchday.
Automatic checks are made by means of Kronos.  
  
  
Steps to setup application:
* register on http://www.football-data.org and get your api key.  
* in module api_connection.py find function url_conn and assign your key to api_key variable.  
* migrate db   
* create superuser  
* install kronos tasks by typing in ./manage.py installtasks
* runserver
* login as superuser
* go to localhost:8000/add_competitions/2017 and check competitions that you want to follow/bet  
* now you can create app user using register button and bet fixtures  
  
Fixtures are updated once every 3 minutes automatically.

Default localhost sites:  
* localhost:8000/add_competitions/{year} page with available competitions for given year,  
only superuser can add competitions.  
* localhost:8000/admin admin panel  
* localhost:8000/competitions main page with listed competitions  
* localhost:8000/competition/{id} page with listed fixtures for competition with given id  
* localhost:8000/login displays form to login to app  
* localhost:8000/logout view that logs out current user
* localhost:8000/register displays form that adds new app user that can make bets
* localhost:8000/bet_fixture/{id} displays form that enables betting fixture with given id  
* localhost:8000/account_details/{id} displays page with account details such as amount of cash, pending/finished bets etc for app user with given id
* localhost:8000/show_team/{id} displays detailed data such as team home/away fixtures etc for team with given id in db.
