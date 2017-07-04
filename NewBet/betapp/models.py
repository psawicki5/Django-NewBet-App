from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Competition(models.Model):
    caption = models.CharField(max_length=128)
    league = models.CharField(max_length=12)
    numberOfMatchdays = models.IntegerField()
    year = models.IntegerField()
    numberOfTeams = models.IntegerField()
    currentMatchday = models.IntegerField()

    def __str__(self):
        return self.caption


class Team(models.Model):
    name = models.CharField(max_length=256)
    crestUrl = models.CharField(max_length=256, null=True, blank=True)
    squadMarketValue = models.CharField(max_length=64, null=True, blank=True)
    code = models.CharField(max_length=12, null=True)
    shortName = models.CharField(max_length=64)
    competition = models.ForeignKey(Competition, null=True)

    def __str__(self):
        return self.name


STATUS_TAB = ((1, "SCHEDULED"),
              (2, "FINISHED")
              )

BET_CHOICES = ((1, 1),
               (2, 2),
               (3, 3)
               )


class Fixture(models.Model):
    homeTeam = models.ForeignKey(Team, related_name='homeTeam')
    awayTeam = models.ForeignKey(Team, related_name='awayTeam')
    status = models.IntegerField(choices=STATUS_TAB, default=1)
    matchday = models.IntegerField()
    competition = models.ForeignKey(Competition, related_name='competition')
    date = models.DateTimeField()
    goalsHomeTeam = models.IntegerField(default=None, null=True, blank=True)
    goalsAwayTeam = models.IntegerField(default=None, null=True, blank =True)
    course_team_home_win = models.FloatField(default=1, blank=True)
    course_team_away_win = models.FloatField(default=1, blank=True)
    course_draw = models.FloatField(default=1, blank=True)
    fixture_result = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return str(self.homeTeam.name + " - " + self.awayTeam.name)


class AppUser(models.Model):
    cash = models.FloatField(validators=[MinValueValidator(0.00)])
    bank_account_number = models.CharField(max_length=64)
    user = models.OneToOneField(User)

    def __str__(self):
        return self.user.username


class Bet(models.Model):
    bet_user = models.ForeignKey(AppUser, related_name="bet_user")
    bet_amount = models.FloatField(validators=[MinValueValidator(0.01)])
    fixture = models.ForeignKey(Fixture, related_name="fixture")
    bet = models.IntegerField(choices=BET_CHOICES)
    bet_course = models.FloatField(default=0)
    bet_result = models.IntegerField(default=0, blank=True)
