from django.shortcuts import render, redirect
from .models import StackPlayer, Stack, Lineup, ExportLineup
from .utls import all_lines

from teams.models import Team
from players.models import Player
# Create your views here.


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


def lineups(request):
    lines, grouped = None, None
    p1, p2 = None, None
    if request.method == "POST":
        p1_id = request.POST.get("p1")
        p2_id = request.POST.get("p2")
        p1 = Player.objects.get(id=p1_id)
        p2 = Player.objects.get(id=p2_id)
        t1 = Team.objects.get(dk_name=p1.team)
        t2 = Team.objects.get(dk_name=p2.team)
        salary = p1.salary + p2.salary
        lines = all_lines(50000-salary)
    pitchers = Player.objects.all_starters()
    cont_dict = {
        "pitchers": pitchers,
        "lines": lines,
        "groups": grouped,
        "p1": p1,
        "p2": p2,
    }
    return render(request, "slate/lineups.html", cont_dict)


def add_lineups(request):
    if request.method == "POST":
        print(request.POST)
    return redirect("slate:lineups")