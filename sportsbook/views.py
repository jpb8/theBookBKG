from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from betslip.models import Slip
from django.views.generic import View, DetailView
from .utls import (get_event_qs, get_ml_gs,
                   get_total_qs, get_sprd_qs,
                   get_featured_games, get_live_sports,
                   event_detail_qs)
from account.models import Account
from betslip.models import PlacedBet
from .models import Event, GameOdds
from django.http import Http404
import json


def index(request):
    if request.user.is_authenticated:
        return redirect('sportsbook:home')
    all_sports = get_live_sports()
    return render(request, 'index.html')


def sportsbook_home(request):
    qs = get_featured_games()
    all_sports = get_live_sports()
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'games': qs,
                 'slip': slip_obj,
                 'sports': all_sports,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/index.html', context=game_dict)


def nfl(request):
    game_qs = get_event_qs("NFL", "Game")
    half_qs = get_event_qs("NFL", "FirstHalf")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    sport_label = "NFL"
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def mlb(request):
    game_qs = get_event_qs("MLB", "Game")
    half_qs = get_event_qs("MLB", "FirstFiveInnings")
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    sport_label = "MLB"
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)

def ncaaf(request):
    game_qs = get_event_qs("NCAAF", "Game")
    half_qs = get_event_qs("NCAAF", "FirstHalf")
    sport_label = "NCAA FOOTBALL"
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def nhl(request):
    qs = get_event_qs("NHL", "Game")
    sport_label = "NHL"
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def ncaab(request):
    game_qs = get_event_qs("NCAAB", "Game")
    half_qs = get_event_qs("NCAAB", "FirstHalf")
    sport_label = "NCAABB"
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def nba(request):
    game_qs = get_event_qs("NBA", "Game")
    half_qs = get_event_qs("NBA", "FirstHalf")
    sport_label = "NBA"
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'first_half_bets': half_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def mma(request):
    game_qs = get_event_qs("MMA", "Game")
    sport_label = "MMA"
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    slip_obj.remove_nonpregame_odds()
    all_sports = get_live_sports()
    slip_bets = slip_obj.odds.all().values_list("odd_id", flat=True)
    game_dict = {'full_game_bets': game_qs,
                 'sport_label': sport_label,
                 'sports': all_sports,
                 'slip': slip_obj,
                 'slip_bets': slip_bets}
    return render(request, 'sportsbook/sportsbook.html', context=game_dict)


def base(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('sportsbook:home')
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            return HttpResponse("invalid login details")

    return render(request, 'base.html', context={})


class EventDetailView(DetailView):
    """ Get Event data """
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('pk')
        context['first'] = GameOdds.objects.get_first(game_id)
        context['last'] = GameOdds.objects.get_last(game_id)
        context['odds'] = event_detail_qs(game_id)
        context['slip'] = Slip.objects.new_or_get(self.request)
        context['sports'] = get_live_sports()
        chart_data = []
        for odd in GameOdds.objects.get_full_event_qs(game_id):
            data_point = dict()
            data_point["x", "y"] = odd.time, odd.total
            chart_data.append(data_point)
        context['chart_data'] = chart_data
        return context


class EventHistoryAjax(View):
    """ Retrun chart data for event """
    def get(self, request, *args, **kwargs):
        game_id = request.GET.get('game_id')
        type = request.GET.get('type')
        data = dict()
        data['all_data'] = []
        if type == "total" and GameOdds.objects.get_full_event_qs(game_id) is not None:
            for odd in GameOdds.objects.get_full_event_qs(game_id):
                single_game = dict()
                single_game['x'] = odd.time
                single_game['y'] = odd.total
                data['all_data'].append(single_game)
            data['title'] = "Game Total History"
        elif type == "handicap" and GameOdds.objects.get_full_event_qs(game_id) is not None:
            for odd in GameOdds.objects.get_full_event_qs(game_id):
                single_game = dict()
                single_game['x'] = odd.time
                single_game['y'] = odd.handicap
                data['all_data'].append(single_game)
            data['title'] = "Game Handicap History"
        elif type == "money-line" and GameOdds.objects.get_full_event_qs(game_id) is not None:
            for odd in GameOdds.objects.get_full_event_qs(game_id):
                single_game = dict()
                single_game['x'] = odd.time
                single_game['y'] = odd.h_line
                data['all_data'].append(single_game)
            data['title'] = "Game Home Money Line History"
        return JsonResponse(data)


class BetValuesAjax(View):
    """ return  data for total at risk charts """
    def get(self, request, *args, **kwargs):
        data = dict()
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


@staff_member_required()
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
