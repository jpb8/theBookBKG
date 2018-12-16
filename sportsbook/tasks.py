import requests
import json
from decimal import *
import pytz
from django.utils import timezone
import datetime
from .models import Event, OddsGroup, Odds
import django
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from django.conf import settings

JSONODDS_API_KEY = getattr(settings, "JSONODDS_API_KEY")

headers = {
    'x-api-key': JSONODDS_API_KEY
}

odds_dict = {
    "h_sprd": "PointSpreadHomeLine",
    "a_sprd": "PointSpreadAwayLine",
    "h_line": "MoneyLineHome",
    "a_line": "MoneyLineAway",
    "over": "OverLine",
    "under": "UnderLine"
}

bet_list = ["Game", "FirstHalf", "FirstPeriod"]


def get_full_game_odds(game):
    for odds in game["Odds"]:
        if odds["OddType"] == "Game":
            return True, odds
    return False, None


# Should probably move this to Class
def create_or_update_event(event, sport):
    try:
        date_time = datetime.datetime.strptime(event["MatchTime"], "%Y-%m-%dT%H:%M:%S")
        utc_date_time = date_time.replace(tzinfo=pytz.utc)
        e, new = Event.objects.update_or_create(game_id=event["ID"],
                                                defaults={
                                                    'sport': sport,
                                                    'start_time': utc_date_time,
                                                    'home': event["HomeTeam"],
                                                    'away': event["AwayTeam"],
                                                })
    except django.db.utils.IntegrityError:
        print("Probably a UNIQUE KEY ERROR")
        return None, False
    return e, new


def create_odds_in_group(e, o, odds_dict):
    odds_list = []
    for key, value in odds_dict.items():
        id_odd = o["ID"] + "-" + key
        odd, new = Odds.objects.update_or_create(odd_id=id_odd,
                                                 defaults={
                                                     'type': key,
                                                     'price': o[value],
                                                     'home': e['HomeTeam']
                                                 })
        odds_list.append(odd)
    return odds_list


def pull_sport_odds(sport):
    try:
        print("PULLING FROM API")
        r = requests.get("https://jsonodds.com/api/odds/{}".format(sport), headers=headers)
        data = r.content
        json_data = json.loads(data.decode("utf-8"))
        print("Successful API CALL")
        print(sport)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
    for e in json_data:
        event, new = create_or_update_event(e, sport)
        for o in e["Odds"]:
            if o["OddType"] in bet_list:
                odds_list = create_odds_in_group(e, o, odds_dict)
                try:
                    total = Decimal(o["TotalNumber"])
                    spread = Decimal(o["PointSpreadHome"])
                    odds_group, is_new = OddsGroup.objects.update_or_create(id=o["ID"],
                                                                            defaults={
                                                                                'type': o["OddType"],
                                                                                'h_sprd': odds_list[0],
                                                                                'a_sprd': odds_list[1],
                                                                                'handicap': spread,
                                                                                'h_line': odds_list[2],
                                                                                'a_line': odds_list[3],
                                                                                'total': total,
                                                                                'over': odds_list[4],
                                                                                'under': odds_list[5],
                                                                                'event': event
                                                                            })
                except django.db.utils.IntegrityError:
                    print("Odds Group Integrity Error")
                print("{} - {} - {} => New: {}".format(event.game_id, event.sport, odds_group.type, is_new))
    print("FINISHED")


def update_results(sport):
    try:
        r = requests.get("https://jsonodds.com/api/results/{}".format(sport), headers=headers)
        data = r.content
        json_data = json.loads(data.decode("utf-8"))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
    for e in json_data:
        if e["OddType"] == "Game":
            try:
                event = Event.objects.get(pk=e['ID'])
                time_now = timezone.now()
                if e["HomeScore"] is None or e["HomeScore"] == "":
                    event.h_score = 0
                else:
                    event.h_score = int(e["HomeScore"])
                if e["AwayScore"] is None or e["AwayScore"] == "":
                    event.a_score = 0
                else:
                    event.a_score = int(e["AwayScore"])
                if e["Final"]:
                    event.live_status = 2
                elif event.start_time < time_now:
                    event.live_status = 1
                else:
                    event.live_status = 0
                event.save()
                print("{} => {}".format(event, event.live_status))
            except Event.DoesNotExist:
                pass
        if e["OddType"] in bet_list:
            try:
                group = OddsGroup.objects.get(pk=e['ID'])
                if e["HomeScore"] is None or e["HomeScore"] == "":
                    group.h_score = 0
                else:
                    group.h_score = int(e["HomeScore"])
                if e["AwayScore"] is None or e["AwayScore"] == "":
                    group.a_score = 0
                else:
                    group.a_score = int(e["AwayScore"])
                if e["Final"]:
                    group.live_status = 2
                elif event.start_time < timezone.now():
                    group.live_status = 1
                else:
                    group.live_status = 0
                group.save()
                print("{} => {}".format(event, event.live_status))
            except OddsGroup.DoesNotExist:
                pass


@db_periodic_task(crontab(minute='*/15'))
def pull_nfl():
    pull_sport_odds("NFL")


@db_periodic_task(crontab(minute='*/15'))
def update_nfl():
    update_results("NFL")


@db_periodic_task(crontab(minute='*/15'))
def pull_ncaaf():
    pull_sport_odds("NCAAF")


@db_periodic_task(crontab(minute='*/15'))
def update_ncaaf():
    update_results("NCAAF")


@db_periodic_task(crontab(minute='0', hour='*/2'))
def pull_nhl():
    pull_sport_odds("NHL")


@db_periodic_task(crontab(minute='0', hour='*/2'))
def update_nhl():
    update_results("NHL")


@db_periodic_task(crontab(minute='*/30'))
def pull_nba():
    pull_sport_odds("NBA")


@db_periodic_task(crontab(minute='*/15'))
def update_nba():
    update_results("NBA")


# @db_periodic_task(crontab(minute='0', hour="*/2"))
# def pull_nccaabb():
#     pull_sport_odds("NCAABB")
#
#
# @db_periodic_task(crontab(minute='0', hour="*/2"))
# def update_ncaabb():
#     update_results("NCAABB")
