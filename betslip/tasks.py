from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from .models import PlacedBet


@db_periodic_task(crontab(minute='*/30', hour='0-23'))
def update_bet_values():
    bets = PlacedBet.objects.filter(status=0)
    for bet in bets:
        bet.update_bet_values()


# @db_periodic_task(crontab(minute='*/5', hour='0-23'))
# def update_bet_times():
#     bets = PlacedBet.objects.filter(status=0)
#     for bet in bets:
#         if bet.start_time is None:
#             bet.start_time = bet.get_earliest_start_time()
#             bet.save()
#             print("{} start time: {}".format(bet, bet.start_time))
