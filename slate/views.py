from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import StackPlayer, Stack, ExportLineup, Punt
from .utls import *
from .tasks import save_lus, refresh_bkg

from teams.models import Team
from teams.tasks import update_projected, manual_live_lu_update
from players.models import Player

pos_swap = {
    "C": "c",
    "1B": "fB",
    "2B": "sB",
    "3B": "tB",
    "SS": "ss",
}


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
        if request.is_ajax():
            user = request.user
            stack = Stack.objects.filter(user=user)
            punts = Punt.objects.filter(user=user)
            cont_dict = {
                "stacks": stack,
                "punts": punts,
            }
            html = render_to_string("players/stack_players.html", cont_dict, request=request)
            response_data = {"html": html}
            print(response_data)
            return JsonResponse(response_data)
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
        if pos == "OF":
            ExportLineup.objects.filter(
                Q(of1=player.name_id) |
                Q(of2=player.name_id) |
                Q(of3=player.name_id)
            ).delete()
        else:
            ExportLineup.objects.filter(**{pos_swap[pos]: player.name_id}).delete()
        if pos2 != "":
            if pos2 == "OF":
                ExportLineup.objects.filter(
                    Q(of1=player.name_id) |
                    Q(of2=player.name_id) |
                    Q(of3=player.name_id)
                ).delete()
            else:
                ExportLineup.objects.filter(**{pos_swap[pos2]: player.name_id}).delete()
    return redirect("slate:lineups")


@login_required(login_url="/")
def update_live_lineups(request):
    manual_live_lu_update()
    return redirect('players:stack_builder')


@login_required(login_url="/")
def team_breakdown(request):
    if request.is_ajax:
        user = request.user
        team_id = request.POST.get("team")
        p_combo, batters, pitchers = team_breakdown_data(team_id, user.pk)
        cont_dict = {
            "p_combo": p_combo,
            "batters": batters,
            "pitchers": pitchers
        }
        html = render_to_string("slate/team_breakdown.html", cont_dict, request=request)
        response_data = {"html": html}
        return JsonResponse(response_data)
    return redirect("slate:lineups")
