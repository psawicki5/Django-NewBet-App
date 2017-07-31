from celery import task
from celery.schedules import crontab
from celery.task import periodic_task

from django.core.mail import send_mail
from django.utils import timezone

from .models import *
from .update_db import update_fixtures, create_team_standing


@task
def bet_created(bet_id):
    """
    Sends email with confirmation of creating new bet
    :param bet_id: int
    :return: True if mail sending was successfull, else False
    """
    bet = Bet.objects.get(id=bet_id)
    bet_owner = bet.bet_user
    user = User.objects.get(id=bet_owner.id)

    subject = "Bet number {}".format(bet.id)
    message = """Hello {}! \n\nYo've made a bet in our betapp. Your bet was
     {} PLN on {} in fixture {}, your course is {}""".format(bet_owner,
                                                             bet.bet_amount,
                                                             bet.bet,
                                                             bet.fixture,
                                                             bet.bet_course)
    mail_sent = send_mail(subject, message, 'admin@newbet.com',
                          [user.email])
    return mail_sent


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


@periodic_task(run_every=(crontab(minute="*/3", hour="*", day_of_month="*",
                                  month_of_year="*")))
def check_fixtures():
    change_status()
    update_fixtures_foo()


