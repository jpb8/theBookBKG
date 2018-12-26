from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, m2m_changed
from decimal import Decimal
from django.utils import timezone
from django.contrib import admin
from django.db.models import Q
import uuid
from sportsbook.models import Odds, Event, OddsGroup
from account.models import Account


class BetSlipManager(models.Manager):
    # Used to get users betslip throught the website
    # is this the same as get_or_create???
    def new_or_get(self, request):
        slip_id = request.session.get('slip_id', None)
        qs = self.get_queryset().filter(id=slip_id)
        if qs.count() == 1:
            new_obj = False
            slip_obj = qs.first()
            if request.user.is_authenticated and slip_obj.user is None:
                slip_obj.user = request.user
                slip_obj.save()
        else:
            slip_obj = Slip.objects.new(user=request.user)
            new_obj = True
            request.session['slip_id'] = slip_obj.id
        return slip_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


# Slip used to hold the bets and and products for user
# Functions like a cart but with bets
class Slip(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    odds = models.ManyToManyField(Odds, blank=True)
    divider = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    due = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = BetSlipManager()

    def __str__(self):
        return str(self.pk)

    # if odds_obj is in cart already, delete else add
    def add_or_remove_odd(self, odds_obj):
        if odds_obj in self.odds.all():
            self.odds.remove(odds_obj)
            added = False
        else:
            self.odds.add(odds_obj)
            added = True
        return added

    # Check to see if the games have started already
    def get_earliest_start_time(self):
        start = timezone.now() + timezone.timedelta(days=365)
        for odd in self.odds.all():
            s = odd.get_event_start_time()
            if s < start:
                start = s
        return start

    def remove_nonpregame_odds(self):
        for odd in self.odds.all():
            if odd.get_event_start_time() < timezone.now():
                self.odds.remove(odd)
        return

    # Creates a PlacedBet and BetValue for all odds in the slip
    def create_straight_bets(self, post):
        total_collected = 0
        for bet in self.odds.all():
            collected = Decimal(post['risk-{}'.format(bet.pk)])
            if collected != 0:
                value = Decimal(collected * bet.get_multiplier())
                new_placed = PlacedBet.objects.create(
                    user=self.user,
                    value=value,
                    divider=self.divider,
                    collected=collected,
                    sum_odds=bet.get_multiplier(),
                    placed=timezone.now(),
                    type="S",
                    start_time=bet.get_event_start_time()
                )
                odd_group = bet.get_odd_group()
                BetValue.objects.create(
                    placed_bet=new_placed,
                    odd=bet,
                    value=value,
                    placed_price=bet.price,
                    type=bet.type,
                    event=odd_group.event,
                    total=odd_group.total,
                    handicap=odd_group.handicap,
                    odd_group=odd_group
                )
                total_collected += collected
        return total_collected

    # Creates Placed with all odds as the parlay values
    def create_parlay(self, post):
        risk_amount = post['parlay-risk-input']
        total = 0
        if risk_amount:
            total = Decimal(risk_amount)
            win = Decimal(total * self.divider)
            new_placed = PlacedBet.objects.create(
                user=self.user,
                value=win,
                divider=self.divider,
                collected=total,
                placed=timezone.now(),
                type="P",
                start_time=self.get_earliest_start_time()
            )
            for bet in self.odds.all():
                bet_value = Decimal(win / (self.divider / bet.get_multiplier()))
                odd_group = bet.get_odd_group()
                BetValue.objects.create(
                    placed_bet=new_placed,
                    odd=bet,
                    value=bet_value,
                    placed_price=bet.price,
                    type=bet.type,
                    event=odd_group.event,
                    total=odd_group.total,
                    handicap=odd_group.handicap,
                    odd_group=odd_group
                )
        return total


# Change receiver for adding odds to betslip
def m2m_changed_slip_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        odds = instance.odds.all()
        divide = 1
        for x in odds:
            mult = x.get_multiplier()
            divide = divide * mult
        if instance.divider != divide:
            instance.divider = divide
            instance.save()


m2m_changed.connect(m2m_changed_slip_receiver, sender=Slip.odds.through)


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.divider > 0 and instance.total > 0:
        instance.due = Decimal(instance.total) / Decimal(instance.divider)
    else:
        instance.due = 0


pre_save.connect(pre_save_cart_receiver, sender=Slip)


class PlacedBetpManager(models.Manager):
    def update_all_bet_values(self):  # does this go here?
        bets = self.get_queryset().all()
        for bet in bets:
            bet.update_bet_values()

    def active(self):
        return self.get_queryset().filter(status=0)

    def total_handle(self):
        return self.active().aggregate(Sum("collected"))

    def total_risk(self):  # Need Raw Sql to get actual risk
        return self.active().aggregate(Sum("value"))


# All placed bets
class PlacedBet(models.Model):
    STATUS_OPTIONS = (
        (0, 'active'),
        (1, 'lose'),
        (2, 'win'),
        (3, 'push')
    )
    TYPE_CHOICES = (
        ("S", "striaght"),
        ("P", "parlay")
    )
    placed_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    odds = models.ManyToManyField(Odds, through="BetValue")
    divider = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    sum_odds = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    placed = models.DateTimeField()
    collected = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    value = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    start_time = models.DateTimeField(null=True)
    status = models.IntegerField(choices=STATUS_OPTIONS, default=0)
    type = models.CharField(max_length=24)

    objects = PlacedBetpManager()

    def __str__(self):
        return "{}: Value: {}".format(self.user, self.value)

    def update_bet_values(self):
        bets = self.betvalue_set.all()
        if bets:
            price_sum = 0
            for bet in bets:
                if bet.status == 0:
                    price_sum += bet.get_multiplier()
                elif bet.status == 2:
                    bet.value = 0
                    bet.save()
            if price_sum != 0:
                for bet in bets:
                    if bet.status == 0:
                        bet.value = Decimal(self.value / (price_sum / bet.get_multiplier()))
                    print(bet)
                    bet.save()
        return

    def update_straight(self):
        if self.status == 0:
            bet = self.betvalue_set.all().first()
            self.status = bet.status
            if self.status == 2 or self.status == 3:
                self.pay_winners_or_push()
            self.save()
        return

    def update_parlay(self):
        if self.status == 0:
            bets = self.betvalue_set.all()
            if bets.filter(status=1).exists():  # if there is losing bet
                bets.update(value=0)
                self.status = 1
                print("{} is a loser".format(self))
            elif bets.filter(status=3).exists():  # If there is bet that isn't final yet
                value = self.updated_value_from_push()
                self.value = value
            if bets.filter(Q(status=2) | Q(status=3)).count() == bets.count():  # All bets will be winners at this point
                print("{} is a winner!!".format(self))
                self.status = 2
                self.pay_winners_or_push()
            self.save()
        return

    def updated_value_from_push(self):
        bets = self.betvalue_set.filter(~Q(status=3))
        multiplier = 1
        if bets:
            for bet in bets:
                multiplier *= bet.get_multiplier()
        return Decimal(self.collected * multiplier)

    def pay_winners_or_push(self):
        account = Account.objects.get(user=self.user)
        if self.status == 2:
            account.reward_bet(self.value)
        elif self.status == 3:
            account.reward_bet(self.collected)
        return

    def check_odds_update_status(self):
        if self.type == "P":
            self.update_parlay()
        elif self.type == "S":
            self.update_straight()
        return

    def cancel_and_refund(self):
        if self.get_earliest_start_time() < timezone.now():
            return False
        else:
            account = Account.objects.get(user=self.user)
            account.reward_bet(self.collected)
            self.delete()
        return True

    def get_earliest_start_time(self):
        start = timezone.now() + timezone.timedelta(days=365)
        for odd in self.odds.all():
            s = odd.get_event_start_time()
            if s < start:
                start = s
        return start


class PlacedBetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'placed_id', 'collected', 'status', 'type')
    list_filter = ('status', 'type')


class BetValueManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(status=0)

    def total_risk(self):  # Need Raw Sql to get actual risk
        return self.active().aggregate(Sum("value"))


class BetValue(models.Model):
    STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'lose'),
        (2, 'win'),
        (3, 'push')
    )
    placed_bet = models.ForeignKey(PlacedBet, on_delete=models.CASCADE)
    odd = models.ForeignKey(Odds, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    odd_group = models.ForeignKey(OddsGroup, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=7, decimal_places=1, null=True)
    handicap = models.DecimalField(max_digits=7, decimal_places=1)
    placed_price = models.IntegerField()
    type = models.CharField(max_length=24)
    status = models.IntegerField(choices=STATUS_OPTIONS, default=0)
    value = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)

    objects = BetValueManager()

    def __str__(self):
        return self.get_display_name()

    # Convert price to tradition odd
    # ex. +150 => 2.5
    def get_multiplier(self):
        multiplier = Decimal(0)
        if self.placed_price > 0:
            multiplier = Decimal(self.placed_price / 100 + 1)
        else:
            multiplier = Decimal(100 / (self.placed_price * -1) + 1)
        return multiplier

    def get_user(self):
        return self.placed_bet.user

    def get_display_name(self):
        event = self.event
        if self.type == "h_sprd":
            return "{} {} ({})".format(event.home, self.handicap, self.placed_price)
        elif self.type == "a_sprd":
            handicap = self.handicap * -1
            return "{} {} ({})".format(event.away, handicap, self.placed_price)
        elif self.type == "h_line":
            return "{} ({})".format(event.home, self.placed_price)
        elif self.type == "a_line":
            return "{} ({})".format(event.away, self.placed_price)
        elif self.type == "over":
            return "Total ({} vs {}) O{} ({})".format(event.away, event.home, self.total, self.placed_price)
        elif self.type == "under":
            return "Total ({} vs {}) U{} ({})".format(event.away, event.home, self.total, self.placed_price)
        return "Unknown"


class BetValueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'value', 'status', 'get_user')
    list_filter = ('status',)


def update_bets(sender, instance, *args, **kwargs):
    instance.placed_bet.check_odds_update_status()


post_save.connect(update_bets, sender=BetValue)
