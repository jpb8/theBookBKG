from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from decimal import Decimal
from sportsbook.models import Odds
from django.core.serializers import serialize
from account.models import Account
from .utls import validate_slip
from django.db import transaction
from django.template.loader import render_to_string

# Create your views here.
def slip_home(request):
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    if slip_obj.divider == 0 or slip_obj.odds.count() == 5:
        min_price = -10000
    else:
        cnt = Decimal(1 / int(5 - slip_obj.odds.count()))
        max_divider = (20 / slip_obj.divider) ** (cnt)
        if max_divider < 2:
            min_price = -100 / (max_divider - 1)
        else:
            min_price = (max_divider - 1) * 100
    odds_list = Odds.objects.filter(price__gte=min_price)
    cont_dict = {
        'slip': slip_obj,
        'odds': odds_list,
    }
    return render(request, 'betslip/home.html', context=cont_dict)


# Update BetSkip with odd or product
# Used in ajax calls in shop/sportsbook templates
def slip_update(request):
    odds_id = request.POST.get('bet_id')
    added = False
    # If odds_id exists, get odd, then get slip and add odd to slip
    if odds_id:
        try:
            odds_obj = Odds.objects.get(odd_id=odds_id)
        except Odds.DoesNotExist:
            print('Odds does not exist')
            return redirect('betslip:home')
        slip_obj, new_obj = Slip.objects.new_or_get(request)
        added = slip_obj.add_or_remove_odd(odds_obj)
        request.session['slip_odds'] = str(round(slip_obj.divider, 2))
        request.session['slip_due'] = str(round(slip_obj.due, 2))
    # Serialize bet and send back with ajax - Old
    # render sidebar template and return it as a string - new
    if request.is_ajax:
        slip_dict = {"slip": slip_obj}
        html = render_to_string("sportsbook/sidebar.html", slip_dict)
        # bets = serialize('json', slip_obj.odds.all())
        # json_data = {
        #     "added": added,
        #     "removed": not added,
        #     "slipOdds": str(round(slip_obj.divider, 2)),
        #     "slipDue": str(round(slip_obj.due, 2)),
        #     "slipTotal": str(round(slip_obj.total, 2)),
        #     "slipMulti": str(round(slip_obj.divider)),
        #     "slipBets": bets,
        # }
        return HttpResponse(html)
    return redirect('betslip:home')


# Update a parlay with either a bet
# used in betslip_home
def parley_update(request):
    # Get bet_id, if exists, get odd
    odds_id = request.POST.get('bet_id')
    if odds_id is not None:
        try:
            odds_obj = Odds.objects.get(odd_id=odds_id)
        except Odds.DoesNotExist:
            print('Odds does not exist')
            return redirect('betslip:home')
        slip_obj, new_obj = Slip.objects.new_or_get(request)
        added = slip_obj.add_or_remove_odd(odds_obj)
        request.session['slip_odds'] = str(round(slip_obj.divider, 2))
        request.session['slip_due'] = str(round(slip_obj.due, 2))
        if request.is_ajax:
            min_price = slip_obj.calc_min_price()
            odds_list = serialize('json', Odds.objects.filter(price__gte=min_price, status=0))
            bets = serialize('json', slip_obj.odds.all())
            json_data = {
                "added": added,
                "removed": not added,
                "slipOdds": str(round(slip_obj.divider, 2)),
                "slipDue": str(round(slip_obj.due, 2)),
                "minPrice": min_price,
                "slipBets": bets,
                "oddsRemain": odds_list,
            }
            return JsonResponse(json_data)
    return redirect('betslip:home')


# Submits all bets
def submit_bet(request):
    if not request.user.is_authenticated:
        return redirect('account:signup')
    try:
        slip_obj, new_obj = Slip.objects.new_or_get(request)
    except Slip.DoesNotExist:
        print('Slip does not exist')
        return redirect('betslip:home')
    if request.method == 'POST':
        post = request.POST
        try:
            account = Account.objects.get(user=request.user)
        except Account.DoesNotExist:
            return redirect('account:signup') # Change to Sign In
        # Check if bet slip is valid
        #   1. Check game start times
        #   2. Check account balance
        #   3. Check account limits
        valid, message = validate_slip(slip_obj, account, post) # Returns Bool for valid and error Message
        if not valid:
            print(message)
            HttpResponse(message)
        else:
            # Create PlacedBets and BetValues
            if "parlay-checkbox" in post:
                slip_obj.create_parlay(post)
            slip_obj.create_straight_bets(request.POST)
            slip_obj.odds.clear()
            # Get account for update and withdraw the total of all the bet.
            with transaction.atomic():
                account_for_withdraw = Account.objects.select_for_update().get(user=request.user)
                due = Decimal(post['betlsip-total-risk'])
                account_for_withdraw.balance -= due
                account_for_withdraw.save()
            return redirect('account:active_bets')
    return redirect('account:active_bets')


def check_out(request):
    if not request.user.is_authenticated:
        return redirect('sportsbook:mlb')
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    cont_dict = {
        'slip': slip_obj,
    }
    return render(request, 'betslip/check_out.html', cont_dict)
