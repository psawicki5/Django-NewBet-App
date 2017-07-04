from django.db import models


class Competition(models.Model):
    caption = models.CharField(max_length=128)
    league = models.CharField(max_length=12)
    numberOfMatchdays = models.IntegerField()
    year = models.IntegerField()
    numberOfTeams = models.IntegerField()
    currentMatchday = models.IntegerField()


class Team(models.Model):


