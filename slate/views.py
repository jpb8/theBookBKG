from django.shortcuts import render, redirect
from .models import StackPlayer, Stack

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
