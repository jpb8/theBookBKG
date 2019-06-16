from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string

import json

from .models import Player
from .tasks import orders, starting_pitchers, upload_stats, upload_salaries, upload_batting_hands, update_projections

from teams.models import Team
from slate.models import Stack, Punt
from slate.utls import todays_stacks, todays_pitchers, tp_utils, stack_utils, pstats, indy_pitcher


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
    pitchers = todays_pitchers()
    tp_data = tp_utils()
    for r in tp_data:
        r['min'] = float(r['min'])
        r['max'] = float(r['max'])
        r['avg'] = float(r['avg'])
        r['std'] = float(r['std'])
    cont_dict = {
        'pitchers': pitchers,
        'cols': json.dumps(tp_data)
    }
    return render(request, "players/pitcher_stats.html", cont_dict)


def stacks_stats(request):
    stacks = todays_stacks()
    stacks_utils = stack_utils()
    for r in stacks_utils:
        r['min'] = float(r['min'])
        r['max'] = float(r['max'])
        r['avg'] = float(r['avg'])
        r['std'] = float(r['std'])
    cont_dict = {
        'stacks': stacks,
        'cols': json.dumps(stacks_utils)
    }
    return render(request, "players/stack_stats.html", cont_dict)


def team_stats(request):
    team = request.POST.get("team")
    pitcher = request.POST.get("pitcher")
    if request.is_ajax:
        pr, pl = indy_pitcher(pitcher)
        cont_dict = {
            'players': pstats(team),
            'pl': pl[0],
            'pr': pr[0],
            'current_team': team
        }
        html = render_to_string("players/pstats.html", cont_dict, request=request)
        response_data = {"html": html}
        return JsonResponse(response_data)
    cont_dict = {
        'players': pstats(team)
    }
    return render(request, "players/pstats.html", cont_dict)


def player_bats(request):
    if request.method == "POST":
        dk_csv = request.FILES["file"]
        if not dk_csv.name.endswith('.csv'):
            error = True  # ???????
        upload_batting_hands(dk_csv)
    cont_dict = {}
    return render(request, "players/stats_upload.html", cont_dict)


def pull_projections(request):
    update_projections()
    return redirect("players:stack_builder")


def stacks_call(request):
    user = request.user
    stack = Stack.objects.filter(user=user)
    punts = Punt.objects.filter(user=user)
    cont_dict = {
        "stacks": stack,
        "punts": punts,
    }
    if request.is_ajax:
        html = render_to_string("players/stack_players.html", cont_dict, request=request)
        response_data = {"html": html}
        print(response_data)
        return JsonResponse(response_data)
    return render(request, "players/stack_players.html", cont_dict)
