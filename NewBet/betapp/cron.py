import kronos

from django.utils import timezone
from .models import *
from .update_db import update_fixtures, create_team_standing


def change_status():
    now = timezone.now()
    fixtures = Fixture.objects.filter(status=1)
    for fixture in fixtures:
        if fixture.date < now:
            fixture.status = 3
            fixture.save()


def update_fixtures_foo():
    competitons = Competition.objects.all()
    for competition in competitons:
        update_fixtures(api_id=competition.api_id)
        create_team_standing(competition_id=competition.id)


@kronos.register('*/3 * * * *')
def check_fixtures():
    change_status()
    update_fixtures_foo()
