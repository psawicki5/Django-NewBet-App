import kronos
from datetime import datetime
from django.utils import timezone

from .models import *
from .update_db import update_fixtures


def change_status():
    now = timezone.now()
    fixtures = Fixture.objects.filter(status=1)
    for fixture in fixtures:
        if fixture.date < now:
            fixture.status = 3
            fixture.save()


@kronos.register('*/5 * * * *')
def check_if_fixture_started():
    change_status()


@kronos.register('*/30 * * * *')
def update_fixtures_periodically():
    update_fixtures()
