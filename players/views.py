from django.shortcuts import render, redirect
import json

from .models import Player
from .tasks import orders, starting_pitchers, upload_stats, upload_salaries, projected_orders

from teams.models import Team
from slate.models import Stack, Punt
from slate.utls import stacks_stats, todays_pitchers, tp_utils


def index(request):
    return render(request, "players/index.html", {})


def upload_player(request):
    if request.method == "POST":
        dk_csv = request.FILES["file"]
        if not dk_csv.name.endswith('.csv'):
            error = True  # ???????
        upload_salaries(dk_csv)
    cont_dict = {}
    return render(request, "players/upload_players.html", cont_dict)


def available_lineups(request):
    cont_dict = {}
    return render(request, "players/upload_players.html", cont_dict)


def stats(request):
    if request.method == "POST":
        for f in request.FILES:
            player_data = request.FILES[f]
            upload_stats(player_data, f)
    return render(request, "players/stats_upload.html", {})


def starters_order(request):
    orders()
    starting_pitchers()
    return redirect("players:upload_players")


def stack_builder(request):
    players = {}
    user = request.user
    current_team = ""
    if request.method == "POST":
        team = request.POST.get("team")
        players = Player.objects.filter(team=team).exclude(position="SP").exclude(position="RP").order_by('-order_pos')
        current_team = team
    teams = Team.objects.filter(on_slate=True).order_by("dk_name")
    stacks = Stack.objects.filter(user=user)
    punts = Punt.objects.filter(user=user)
    cont_dict = {
        "teams": teams,
        "players": players,
        "stacks": stacks,
        "punts": punts,
        "current_team": current_team,
    }
    return render(request, "players/stack_builder.html", cont_dict)


def pitching_stats(request):
    # pitchers = todays_pitchers()
    tp_data = tp_utils()
    cols = []
    for t in tp_data:
        col = {}
        col["row"] = int(t["numb"])
        col["var_arr"], col["opac_arr"] = opacity(10, t["min"], t["max"])
        cols.append(col)
    print(cols)
    cont_dict = {
        'cols': json.dumps(cols)
    }
    return render(request, "players/pitcher_stats.html", cont_dict)


def opacity(n, minn, maxx):
    diff = maxx - minn
    var_div = diff / n
    opac_div = round(1 / n, 2)
    var_arr = []
    opac_arr = []
    for i in range(n - 1):
        var_arr.append(round(float(var_div * (i + 1) + minn), 4))
        opac_arr.append(round(float(opac_div * (i + 1)), 2))
    return var_arr, opac_arr
