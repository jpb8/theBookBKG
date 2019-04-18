from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StackPlayer, Stack, ExportLineup, Punt
from .utls import *
from .tasks import save_lus, refresh_bkg

from teams.models import Team
from teams.tasks import update_projected
from players.models import Player


# Create your views here.

@login_required(login_url="/")
def stack_add(request):
    if request.method == "POST":
        user = request.user
        team_id = request.POST.get("team")
        team = Team.objects.get(dk_name=team_id)
        stack, created = Stack.objects.get_or_create(user=user, team=team)
        i = 1 if not stack.players.all().exists() else stack.players.all().count() + 1
        for p_id, key in request.POST.items():
            if key == "player":
                p = Player.objects.get(id=int(p_id))
                if not StackPlayer.objects.filter(stack=stack, player=p).exists():
                    sp = StackPlayer(stack=stack, player=p, order_spot=i)
                    sp.save()
                    i += 1
    return redirect('players:stack_builder')


@login_required(login_url="/")
def remove(request):
    user = request.user
    if request.method == "POST":
        for p_id, key in request.POST.items():
            if key == "player":
                StackPlayer.objects.get(pk=int(p_id)).delete()
        stacks = Stack.objects.filter(user=user)
        for s in stacks:
            if not s.players.all().exists():
                s.delete()
            else:
                for i, p in enumerate(s.players.all(), start=1):
                    p.order_spot = i
                    p.save()
    return redirect('players:stack_builder')


@login_required(login_url="/")
def lineups(request):
    lines, pplay = None, None
    p1, p2 = None, None
    if request.method == "POST":
        p1_id = request.POST.get("p1")
        p2_id = request.POST.get("p2")
        p1 = Player.objects.get(id=p1_id)
        p2 = Player.objects.get(id=p2_id)
        salary = p1.salary + p2.salary
        lines = all_lines(50000 - salary, punt=False)
        pplay = all_lines(50000 - salary, punt=True)
    user = request.user
    pitchers = Player.objects.all_starters()
    groups = ExportLineup.objects.group(user)
    saved_lus = tm_cnt(user.pk)
    p_cnt = pitcher_cnt(user.pk)
    h_cnt = hitter_cnt(user.pk)
    total_lus = 0
    for p in p_cnt:
        total_lus += int(p["cnt"])
    total_lus = total_lus * 0.5
    cont_dict = {
        "pitchers": pitchers,
        "lines": lines,
        "pplays": pplay,
        "saved_lus": saved_lus,
        "p_cnt": p_cnt,
        "total_lus": total_lus,
        "h_cnt": h_cnt,
        "groups": groups,
        "p1": p1,
        "p2": p2,
    }
    return render(request, "slate/lineups.html", cont_dict)


@login_required(login_url="/")
def add_lineups(request):
    if request.method == "POST":
        save_lus(request.POST, request.user)
    return redirect("slate:lineups")


@login_required(login_url="/")
def delete_all(request):
    ExportLineup.objects.filter(user=request.user).delete()
    return redirect("slate:lineups")


@login_required(login_url="/")
def update_pro_orders(request):
    update_projected()
    return redirect("players:index")


@login_required(login_url="/")
def lineup_check(request):
    cont_dict = {
        "players": not_in_order_players(request.user.pk)
    }
    return render(request, "slate/lineup_check.html", cont_dict)


@login_required(login_url="/")
def refresh_big_kahuna(request):
    refresh_bkg()
    return redirect("slate:lineups")


@login_required(login_url="/")
def add_punts(request):
    if request.method == "POST":
        user = request.user
        for p_id, key in request.POST.items():
            if key == "player":
                p = Player.objects.get(id=int(p_id))
                if not Punt.objects.filter(user=user, dkid=p.dkid).exists():
                    sp = Punt(user=user, dkid=p.dkid, name_id=p.name_id, position=p.position, salary=p.salary)
                    sp.save()
                else:
                    Punt.objects.filter(user=user, dkid=p.dkid).delete()
    return redirect('players:stack_builder')


@login_required(login_url="/")
def remove_punts(request):
    if request.method == "POST":
        for p_id, key in request.POST.items():
            if key == "player":
                Punt.objects.get(pk=int(p_id)).delete()
    return redirect('players:stack_builder')


@login_required(login_url="/")
def delete_bad_lines(request):
    bad_players = not_in_order_players(request.user.pk)
    for p in bad_players:
        player = Player.objects.get(name_id=p["p"])
        pos = player.position
        pos2 = player.position
        ExportLineup.objects.filter(**{pos: player.name_id}).delete()
        if pos2 != "":
            ExportLineup.objects.filter(**{pos2: player.name_id}).delete()
    return redirect("slate:lineups")
