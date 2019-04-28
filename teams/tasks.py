from bs4 import BeautifulSoup
import requests
from .models import Team, DefaultOrders
from players.models import Player
from huey.contrib.djhuey import db_task, db_periodic_task
from huey import crontab

matchup_mapper = {
    "Default vs. RHP": "R",
    "Default vs. LHP": "L",
    "Interleague vs. RHP": "ILR",
    "Interleague vs. LHP": "ILR"
}


def get_pro_lineups(team):
    url = "https://www.rotowire.com/baseball/batting-orders.php?team={}".format(team)
    data = requests.get(url)
    soup = BeautifulSoup(data.text, "html.parser")
    return get_names(soup.find_all("div", class_="col border-rb mb-20"))


def get_names(pro_lineups):
    dict = {}
    for l in pro_lineups:
        lu_type = l.find('div', class_="border-tb heading-primary bg-cod-gray white pad-5-10").text.strip()
        dict[lu_type] = {}
        player = l.find_all("li", class_="md-text")
        for i, p in enumerate(player, start=1):
            a = p.find("a")
            dict[lu_type][i] = a.text.strip()
    return dict


@db_task()
def update_projected():
    all_teams = Team.objects.all()
    for t in all_teams:
        projected_lineups = get_pro_lineups(t.dk_name)
        for k, v in projected_lineups.items():
            if k in matchup_mapper:
                game_type = matchup_mapper[k]
                print(game_type)
                for o, p in v.items():
                    print(o, p)
                    DefaultOrders.objects.filter(
                        team=t,
                        game_type=game_type,
                        order=o
                    ).update(rw_name=p)


@db_task()
@db_periodic_task(crontab(minute='*/10', hour='19-22'))
def update_live_lus():
    on_slate = Team.objects.on_slate()
    non_slate_teams = Team.objects.filter(on_slate=False)
    for t in non_slate_teams:
        Player.objects.filter(team=t.dk_name).update(order_pos=0)
    for t in on_slate:
        projected_lineups = get_pro_lineups(t.dk_name)
        order = projected_lineups["Today's Lineup"] if "Today's Lineup" in projected_lineups else None
        if len(order) > 1:
            Player.objects.filter(team=t.dk_name).update(order_pos=0)
            for o, p in order.items():
                print(o, p, t)
                Player.objects.filter(rotowire_name=p, team=t.dk_name).update(order_pos=o)
