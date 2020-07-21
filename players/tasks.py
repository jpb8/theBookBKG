from .models import Player, Pitching, Batting
from huey.contrib.djhuey import db_task, db_periodic_task
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from django.db.models import Q
from jsonodds.odds import Odds

import json
from datetime import datetime as dt
import pytz
from decimal import Decimal
from scipy import stats
import math
import statistics

from teams.models import Team, DefaultOrders
from slate.utls import update_players_projections, projections_for_ownership, update_team_pown
import csv
import io

JSONODDS_API_KEY = getattr(settings, "JSONODDS_API_KEY")

stat_type = {
    'pall': 2,
    'pr': 0,
    'pl': 1,
    'ps': 3,
    'ball': 2,
    'br': 0,
    'bl': 1,
    'bs': 3,
    'tr': 0,
    'tl': 1
}


def get_lineups():
    url = "https://www.rotowire.com/baseball/daily-lineups.php"
    data = requests.get(url)
    soup = BeautifulSoup(data.text, "html.parser")
    return team_lineups(soup.find_all("div", class_="lineup"))


def team_lineups(lineups):
    all_lineups = {}
    for l in lineups:
        home_team, away_team = get_teams(l)
        if l.find_all("div", {"class": ["lineup__main"]}):
            main = l.find("div", {"class": ["lineup__main"]})
            home = main.find("ul", {"class": ["is-home"]})
            away = main.find("ul", {"class": ["is-visit"]})
            if home and away:
                home_lu = players(home.find_all("li", class_="lineup__player"))
                away_lu = players(away.find_all("li", class_="lineup__player"))
                all_lineups[home_team] = home_lu
                all_lineups[away_team] = away_lu
    return all_lineups


def players(team):
    players = {}
    for index, t in enumerate(team, start=1):
        if t.find("a"):
            a = t.find("a")
            players[index] = a.get("title").strip()
    return players


def get_teams(lineup):
    home = ""
    away = ""
    if lineup.find_all("div", class_="lineup__abbr"):
        away = lineup.find_all("div", class_="lineup__abbr")[0].text.strip()
        home = lineup.find_all("div", class_="lineup__abbr")[1].text.strip()
    return home, away


def update_batting_order(team_orders):
    for t, v in team_orders.items():
        for o, n in v.items():
            print(o, n)
            Player.objects.filter(rotowire_name=n).update(order_pos=int(o))


def projected_orders():
    Player.objects.all().update(order_pos=0)
    teams = Team.objects.filter(on_slate=True)
    for t in teams:
        throws = Player.team_starter_trows(t.opp)
        opp = Team.objects.get(dk_name=t.opp)
        game_type = throws if throws != "" else "R"
        if not t.home and opp.league != t.league:
            game_type = "IL" + throws
        p_orders = DefaultOrders.objects.projected(team=t, game_type=game_type)
        for p in p_orders:
            Player.objects.filter(rotowire_name=p.rw_name, active=True).update(order_pos=p.order)
            print(p)


@db_task()
def starting_pitchers():
    mlb = Odds(JSONODDS_API_KEY).get_odds("MLB")
    data = mlb.content
    json_data = json.loads(data.decode("utf-8"))
    Player.objects.all().update(starting=False)
    for e in json_data:
        start = Team.objects.get(fg_name=e["HomeTeam"]).start_time
        home = e["HomePitcher"] if "HomePitcher" in e else None
        away = e["AwayPitcher"] if "AwayPitcher" in e else None
        date_time = dt.strptime(e["MatchTime"], "%Y-%m-%dT%H:%M:%S")
        utc_dt = date_time.replace(tzinfo=pytz.utc)
        if start == utc_dt:
            print("{} and {} starting for {} and {} @ {}".format(home, away, e["HomeTeam"], e["AwayTeam"], start))
            Player.objects.filter(Q(dk_name=home) | Q(dk_name=away)).update(starting=True)
        else:
            print("Game Not on slate")


@db_task()
def upload_salaries(dk_csv):
    player_data = dk_csv.read().decode('UTF-8')
    io_string = io.StringIO(player_data)
    next(io_string)
    Player.upload_dk(csv.reader(io_string, delimiter=','))
    projected_orders()


@db_task()
def upload_stats(player_data, filename):
    _csv = player_data.read().decode('UTF-8')
    io_string = io.StringIO(_csv)
    next(io_string)
    csv_data = csv.reader(io_string, delimiter=',')
    hand = stat_type[filename]
    print(filename[0])
    if filename[0] == 'p':
        Pitching.upload(csv_data, hand)
    elif filename[0] == 'b':
        Batting.upload(csv_data, hand)
    else:
        Batting.upload_team(csv_data, hand)


@db_task()
def upload_batting_stats(csv_data, hand):
    Pitching.upload(csv_data, hand)


@db_task()
def orders():
    projected_orders()


@db_task()
def upload_batting_hands(player_data):
    _csv = player_data.read().decode('UTF-8')
    io_string = io.StringIO(_csv)
    next(io_string)
    csv_data = csv.reader(io_string, delimiter=',')
    for r in csv_data:
        try:
            Player.objects.filter(rotowire_name=str(r[0])).update(bats=str(r[1]))
            print(Player.objects.filter(rotowire_name=str(r[0])).fg_name, r[0], r[1])
        except Player.DoesNotExist:
            print("No player")


@db_task()
def update_projections():
    url = "https://rotogrinders.com/projected-stats/mlb-hitter.csv?site=draftkings"
    data = requests.get(url)
    io_string = io.StringIO(data.text)
    csv_data = csv.reader(io_string, delimiter=',')
    for p in csv_data:
        Player.objects.filter(rotowire_name=str(p[0])).update(pts=Decimal(p[7]))
        print(p[0], p[7])


@db_task()
def pown(pown_data):
    _csv = pown_data.read().decode('UTF-8')
    io_string = io.StringIO(_csv)
    next(io_string)
    csv_data = csv.reader(io_string, delimiter=',')
    Player.objects.all().update(pown=0.0)
    for r in csv_data:
        try:
            Player.objects.filter(dk_name=str(r[0])).update(pown=Decimal(r[1]))
            print(Player.objects.filter(dk_name=str(r[0])), r[0], r[1])
        except Player.DoesNotExist:
            print("No player")


def remove_low_own_players(pos_stats):
    median = statistics.median(pos_stats.values())
    new = {}
    for p, pown in pos_stats.items():
        if pown >= median:
            new[p] = pown
    return new


def calc_final_pos_pown(pos_stats, pos):
    new_pstat = remove_low_own_players(pos_stats)
    total_prob = sum(new_pstat.values())
    for play, prob in new_pstat.items():
        divider = 1 if pos == "OF" else 3
        new_pstat[play] = (prob / total_prob) / divider
    return new_pstat


def build_pown(pstats):
    positions = pstats.pos.unique()
    final_player_pown = {}
    for pos in positions:
        plays = pstats.loc[pstats["pos"] == pos]
        tiles = plays.tri.unique()
        pos_final_pown = {}
        for tile in tiles:
            players_in_tile = plays.loc[plays["tri"] == tile]
            pos_stats = {}
            for i, player in players_in_tile.iterrows():
                compare = players_in_tile.drop([i, ])
                prob = 1
                for i2, p in compare.iterrows():
                    mean = player.dkproj - p.dkproj
                    std = math.sqrt((player.ptsstd ** 2) + (p.dkproj ** 2))
                    std = 1 if std == 0 else std
                    prob *= stats.norm.cdf(float(mean) / std)
                pos_stats[player.name_id] = prob
            pos_pown = calc_final_pos_pown(pos_stats, pos)
            pos_final_pown.update(pos_pown)
        final_player_pown.update(pos_final_pown)
    return final_player_pown

@db_task()
def update_projected_ownership_full():
    update_players_projections()
    Player.update_proj_pown(build_pown(projections_for_ownership()))
    update_team_pown()
