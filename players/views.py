from django.shortcuts import render, redirect
from .models import Player
from slate.models import Lineup
from .tasks import orders, starting_pitchers, upload_stats, upload_salaries, projected_orders

from teams.models import Team
from slate.models import Stack


def index(request):
    return render(request, "players/index.html", {})


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
    teams = Team.objects.filter(on_slate=True)
    stacks = Stack.objects.filter(user=user)
    projected_orders()
    cont_dict = {
        "teams": teams,
        "players": players,
        "stacks": stacks,
        "current_team": current_team,
    }
    return render(request, "players/stack_builder.html", cont_dict)
