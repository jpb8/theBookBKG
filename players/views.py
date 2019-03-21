from django.shortcuts import render
from .models import Player, DkGame, Pitching
from teams.models import Team
from slate.models import Lineup
from .tasks import get_lineups, update_batting_order, starting_pitchers, upload_stats, upload_salaries


import csv
import io


# Create your views here.
def upload_player(request):
    if request.method == "POST":
        dk_csv = request.FILES["file"]
        if not dk_csv.name.endswith('.csv'):
            error = True  # ???????
        upload_salaries(dk_csv)
    pitchers = Player.objects.all_starters()
    games = Player.objects.get_games()
    lines = Lineup.objects.under_sal(salary=20000)
    all_active = Player.objects.exclude(order_pos=0).order_by("team", "order_pos")
    cont_dict = {
        "games": games,
        "pitchers": pitchers,
        "lines": lines,
        "players": all_active,
    }
    return render(request, "players/upload_players.html", cont_dict)


def available_lineups(request):
    salary = 0
    if request.method == "POST":
        p1_id = request.POST.get("p1")
        p2_id = request.POST.get("p2")
        p1 = Player.objects.get(id=p1_id)
        p2 = Player.objects.get(id=p2_id)
        salary = p1.salary + p2.salary
    pitchers = Player.objects.all_starters()
    games = Player.objects.get_games()
    lines = Lineup.objects.under_sal(salary=salary)
    cont_dict = {
        "games": games,
        "pitchers": pitchers,
        "lines": lines,
    }
    return render(request, "players/upload_players.html", cont_dict)


def stats(request):
    if request.method == "POST":
        for f in request.FILES:
            player_data = request.FILES[f]
            upload_stats(player_data, f)
    starting_pitchers()
    return render(request, "players/stats_upload.html", {})