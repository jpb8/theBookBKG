from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StackPlayer, Stack, Lineup, ExportLineup
from .utls import all_lines
from .tasks import save_lus

from teams.models import Team
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
    lines = None
    p1, p2 = None, None
    if request.method == "POST":
        p1_id = request.POST.get("p1")
        p2_id = request.POST.get("p2")
        p1 = Player.objects.get(id=p1_id)
        p2 = Player.objects.get(id=p2_id)
        salary = p1.salary + p2.salary
        lines = all_lines(50000 - salary)
    user = request.user
    pitchers = Player.objects.all_starters()
    saved_lus = ExportLineup.objects.group(user)
    cont_dict = {
        "pitchers": pitchers,
        "lines": lines,
        "saveed_lus": saved_lus,
        "p1": p1,
        "p2": p2,
    }
    return render(request, "slate/lineups.html", cont_dict)


@login_required(login_url="/")
def add_lineups(request):
    if request.method == "POST":
        print(request.POST)
        save_lus(request.POST, request.user)
    return redirect("slate:lineups")
