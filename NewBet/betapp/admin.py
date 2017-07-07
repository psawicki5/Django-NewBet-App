from django.contrib import admin
from .models import *


class FixtureAdmin(admin.ModelAdmin):
    list_display = ['id', 'matchday', 'home_team', 'away_team', 'goals_home_team',
                    'goals_away_team']
    search_fields = ['matchday', 'home_team__name', 'away_team__name']


class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'bet_user', 'bet_amount', 'fixture', 'bet',
                    'bet_course', 'bet_result']

    #search_fields = ['fixture', 'bet_user__user__username']

admin.site.register(Competition)
admin.site.register(Team)
admin.site.register(Fixture, FixtureAdmin)
admin.site.register(AppUser)
admin.site.register(Bet, BetAdmin)
