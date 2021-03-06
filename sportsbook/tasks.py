import requests
import json
from decimal import *
import pytz
from django.utils import timezone
import datetime
from .models import Event, OddsGroup, Odds, GameOdds
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

bet_list = ["Game", "FirstHalf", "FirstPeriod", "FirstFiveInnings"]


def get_full_game_odds(game):
    """ loop through list of odds and return game OddsGroup """
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


def get_or_create_gameodds(event, o):
    try:
        game_stat, new = GameOdds.objects.get_or_create(event=event,
                                                        h_line=o["MoneyLineHome"],
                                                        a_line=o["MoneyLineAway"],
                                                        total=Decimal(o["TotalNumber"]),
                                                        handicap=Decimal(o["PointSpreadHome"]),
                                                        )
    except django.db.utils.IntegrityError:
        print("Error happened adding GameOdds")
        return False, False
    return game_stat, new


def pull_sport_odds(sport):
    """ pull events for a given sport and create new Event, OddsGroup, and Odds if it doesn't exsist """
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
                                                                                'h_sprd_price': o[
                                                                                    "PointSpreadHomeLine"],
                                                                                'a_sprd': odds_list[1],
                                                                                'a_sprd_price': o[
                                                                                    "PointSpreadAwayLine"],
                                                                                'handicap': spread,
                                                                                'h_line': odds_list[2],
                                                                                'h_line_price': o["MoneyLineHome"],
                                                                                'a_line': odds_list[3],
                                                                                'a_line_price': o["MoneyLineAway"],
                                                                                'total': total,
                                                                                'over': odds_list[4],
                                                                                'over_price': o["OverLine"],
                                                                                'under': odds_list[5],
                                                                                'under_price': o["UnderLine"],
                                                                                'event': event
                                                                            })
                except django.db.utils.IntegrityError:
                    print("Odds Group Integrity Error")
                if o["OddType"] == "Game" and sport in ("NFL", "NBA", "NCAAF", "MMA", "MLB"):
                    game_stats, new = get_or_create_gameodds(event, o)
                    if new:
                        print(game_stats)
                print("{} - {} - {} => New: {}".format(event.game_id, event.sport, odds_group.type, is_new))
    print("FINISHED")


def update_results(sport):
    """ pull results for a given sport from JsonOdds and update events and OddsGroups """
    try:
        r = requests.get("https://jsonodds.com/api/results/{}".format(sport), headers=headers)
        data = r.content
        json_data = json.loads(data.decode("utf-8"))
        print("Updating {}".format(sport))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
    for e in json_data:
        if e["OddType"] == "Game":  # Update Event data with full game data
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
                if e["Final"] and e["FinalType"] == "Finished":
                    event.live_status = 2
                    print("{} => {}".format(event, event.live_status))
                elif e["Final"] and e["FinalType"] != "Finished":
                    print("{} is canceled".format(event))
                    event.live_status = 3
                elif event.start_time < time_now:
                    event.live_status = 1
                else:
                    event.live_status = 0
                event.save()
            except Event.DoesNotExist:
                pass
        if e["OddType"] in bet_list:  # Only update Game and First Half
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
                if e["Final"] and e["FinalType"] == "Finished":
                    group.live_status = 2
                    print("{} => {}".format(group, group.live_status))
                elif e["Final"] and e["FinalType"] != "Finished":
                    print("{} is canceled".format(group))
                    group.live_status = 3
                elif group.event.start_time < timezone.now():
                    group.live_status = 1
                else:
                    group.live_status = 0
                group.save()
            except OddsGroup.DoesNotExist:
                pass


def active_events(sport):
    events = Event.objects.filter(live_status__in=[0, 1], sport=sport)
    if events:
        earliest = events.earliest('start_time')
        if earliest.start_time < timezone.now():
            return True
    return False


# @db_periodic_task(crontab(minute='*/30'))
# def pull_nfl():
#     pull_sport_odds("NFL")
#
#
# @db_periodic_task(crontab(minute='*/30'))
# def update_nfl():
#     if active_events("NFL"):
#         print("NFL is active")
#         update_results("NFL")
#     else:
#         print("NFL is inactive")


# @db_periodic_task(crontab(minute='*/30'))
# def pull_ncaaf():
#     pull_sport_odds("NCAAF")
#
#
# @db_periodic_task(crontab(minute='*/30'))
# def update_ncaaf():
#     if active_events("NCAAF"):
#         print("NCAA is active")
#         update_results("NCAAF")
#     else:
#         print("NCAA is inactive")


# @db_periodic_task(crontab(minute='0', hour='*/3'))
# def pull_nhl():
#     pull_sport_odds("NHL")
#
#
# @db_periodic_task(crontab(minute='*/30'))
# def update_nhl():
#     if active_events("NHL"):
#         print("NHL is active")
#         update_results("NHL")
#     else:
#         print("NHL is inactive")


# @db_periodic_task(crontab(minute='*/90'))
# def pull_nba():
#     pull_sport_odds("NBA")


# @db_periodic_task(crontab(minute='*/30'))
# def update_nba():
#     if active_events("NBA"):
#         print("NBA is active")
#         update_results("NBA")
#     else:
#         print("NBA is inactive")


@db_periodic_task(crontab(minute='*/90'))
def pull_mlb():
    pull_sport_odds("MLB")


@db_periodic_task(crontab(minute='*/90'))
def update_mlb():
    if active_events("MLB"):
        print("NBA is active")
        update_results("MLB")
    else:
        print("NBA is inactive")


# @db_periodic_task(crontab(minute='0', hour="*/2"))
# def pull_nccaabb():
#     pull_sport_odds("NCAAB")
#
#
# @db_periodic_task(crontab(minute='*/10'))
# def update_ncaabb():
#     if active_events("NCAAB"):
#         print("NCAAB is active")
#         update_results("NCAAB")
#     else:
#         print("NCAAB is inactive")


# @db_periodic_task(crontab(minute='0', hour="*/3"))
# def pull_mma():
#     pull_sport_odds("MMA")
#
#
# @db_periodic_task(crontab(minute='*/30'))
# def update_mma():
#     if active_events("MMA"):
#         print("MMA is active")
#         update_results("MMA")
#     else:
#         print("MMA is inactive")
