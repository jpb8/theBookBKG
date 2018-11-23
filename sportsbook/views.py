from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from betslip.models import Slip
from django.views.generic import View
from .utls import (get_event_qs,
                   get_ml_gs,
                   get_total_qs,
                   get_sprd_qs,
                   get_featured_games)
from account.models import Account
from betslip.models import PlacedBet, BetValue


def index(request):
    return render(request, 'index.html')


def sportsbook_home(request):
    qs = get_featured_games()
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'games': qs,
                 'slip': slip_obj}
    return render(request, 'sportsbook/index.html', context=game_dict)


def nfl(request):
    game_qs = get_event_qs("NFL", "Game")
    half_qs = get_event_qs("NFL", "FirstHalf")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'slip': slip_obj}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def ncaaf(request):
    game_qs = get_event_qs("NCAAF", "Game")
    half_qs = get_event_qs("NCAAF", "FirstHalf")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'slip': slip_obj}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def nhl(request):
    qs = get_event_qs("NHL", "Game")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'games': qs,
                 'slip': slip_obj}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def nba(request):
    game_qs = get_event_qs("NBA", "Game")
    half_qs = get_event_qs("NBA", "FirstHalf")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'slip': slip_obj}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def base(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            return HttpResponse("invalid login details")

    return render(request, 'base.html', context={})


class BetValuesAjax(View):
    def get(self, request, *args, **kwargs):
        data = {}
        data['labels'] = []
        data['data'] = []
        if request.GET.get('type') == 'sprd':
            for e in get_sprd_qs():
                data['labels'].append("{} {}".format(e.team, e.handicap))
                data['data'].append(e.val)
            data['title'] = 'Spread'
        if request.GET.get('type') == 'ou':
            for e in get_total_qs():
                data['labels'].append("{} {}{}".format(e.game_name, e.ou, e.tot))
                data['data'].append(e.val)
            data['title'] = 'Over/Under'
        if request.GET.get('type') == 'line':
            for e in get_ml_gs():
                data['labels'].append(e.team)
                data['data'].append(e.val)
            data['title'] = 'Money Line'
        return JsonResponse(data)


def event_values(request):
    sprd = get_sprd_qs()
    tots = get_total_qs()
    ml = get_ml_gs()
    total = 0
    for e in sprd:
        total += e.val
    for e in tots:
        total += e.val
    for e in ml:
        total += e.val
    event_dict = {
        'events_h_sprd': sprd,
        'total_values': tots,
        'line_values': ml,
        'total_balance': Account.objects.total_balances(),
        'total_handle': PlacedBet.objects.total_handle(),
        'total_risk': total
    }
    return render(request, 'sportsbook/values.html', context=event_dict)
