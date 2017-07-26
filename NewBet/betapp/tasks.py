from celery import task

from django.core.mail import send_mail
from django.contrib.auth.models import User

from .models import Bet

@task
def bet_created(bet_id):
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
