from .models import Player, Pitching, Batting
from huey.contrib.djhuey import db_task
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from jsonodds.odds import Odds
import json

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


def starting_pitchers():
    mlb = Odds(JSONODDS_API_KEY).get_odds("MLB")
    data = mlb.content
    json_data = json.loads(data.decode("utf-8"))
    pitchers = []
    for e in json_data:
        pitchers.append(e["HomePitcher"]) if "HomePitcher" in e else None
        pitchers.append(e["AwayPitcher"]) if "AwayPitcher" in e else None
    Player.objects.all().update(starting=False)
    Player.objects.filter(dk_name__in=pitchers).update(starting=True)


@db_task
def upload_salaries(csv):
    Player.upload_dk(csv)


def upload_stats(csv_data, filename):
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
