from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from account.forms import UserForm, AccountInfoForm
from django.views.generic import UpdateView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .utls import get_client_ip
from .models import Account
from betslip.models import PlacedBet

import datetime
from decimal import Decimal


def signup(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        account_form = AccountInfoForm(request.POST)
        if user_form.is_valid() and account_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            account = account_form.save(commit=False)
            account.user = user
            if 'profile_pic' in request.FILES:
                account.profile_pic = request.FILES['profile_pic']
            account.save()
            return HttpResponseRedirect(reverse('sportsbook:home'))
        else:
            pass
    else:
        user_form = UserForm()
        account_form = AccountInfoForm()

    return render(request, 'account/signup.html',
                  {'user_form': user_form,
                   'account_form': account_form,
                   'registered': registered})


@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def user_login(request):
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
            print('Someone tried to login and failed')
            print('User: {} and password: {}'.format(username, password))
            return HttpResponse("invalid login details")

    return render(request, 'account/user_login.html')


def account_home(request):
    if not request.user.is_authenticated:
        return redirect('account:signup')

    account = Account.objects.get(user=request.user)

    context = {
        'account': account,
    }

    return render(request, 'account/index.html', context)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    fields = ('profile_pic', 'address', 'city', 'state', 'zip_code')
    model = Account


class AccountDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'account_detail'
    model = Account
    template_name = 'account/account_detail.html'


def active_bets(request):
    if not request.user.is_authenticated:
        return redirect('sportsbook:mlb')
    user = request.user
    time_48_hours_ago = datetime.datetime.now() - datetime.timedelta(days=2)
    placed_bets = PlacedBet.objects.filter(user=user,
                                           placed__gte=time_48_hours_ago)
    bet_dict = {
        'placed_bets': placed_bets,
    }
    return render(request, 'account/active_bets.html', bet_dict)


@login_required(login_url="/")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account:account_home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})
