from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from .models import PlacedBet


@db_periodic_task(crontab(minute='*/30', hour='0-23'))
def update_bet_values():
    bets = PlacedBet.objects.filter(status=0)
    for bet in bets:
        bet.update_bet_values()
