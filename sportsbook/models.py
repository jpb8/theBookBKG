from django.db import models
from django.db.models.signals import post_save
from decimal import Decimal
from django.contrib import admin
from django.db.models import Max, Min


class OddsManager(models.Manager):
    def get_all_active(self):
        return self.get_queryset().filter(status=0)


# Odds for event
# connected by one2one keys on event
# need to add odds Tpye for Gmae, 1st half, 2nd half, ect
class Odds(models.Model):
    BET_TYPES = (
        ('h_sprd', 'Home Spread'),
        ('a_sprd', 'Away Spread'),
        ('h_line', 'Home Line'),
        ('a_line', 'Away Line'),
        ('over', 'Over'),
        ('under', 'Under'),
    )

    ODDS_STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'lose'),
        (2, 'win'),
        (3, 'push')
    )

    odd_id = models.CharField(max_length=100, primary_key=True)
    home = models.CharField(max_length=48, null=True)
    type = models.CharField(max_length=24, choices=BET_TYPES)
    price = models.IntegerField()
    status = models.IntegerField(choices=ODDS_STATUS_OPTIONS, default=0)  # DELETE?

    objects = models.Manager()
    active_objects = OddsManager()

    class Meta:
        verbose_name_plural = "Odds"

    def __str__(self):
        return "{} Type: {}".format(self.home, self.type)

    def get_display_name(self):
        odd_group = self.get_odd_group()
        event = self.get_event()
        if self.type == "h_sprd":
            return "{} {} ({})".format(self.home, odd_group.handicap, self.price)
        elif self.type == "a_sprd":
            handicap = odd_group.handicap * -1
            return "{} {} ({})".format(event.away, handicap, self.price)
        elif self.type == "h_line":
            return "{} ({})".format(self.home, self.price)
        elif self.type == "a_line":
            return "{} ({})".format(event.away, self.price)
        elif self.type == "over":
            return "Total ({} vs {}) O{} ({})".format(event.away, event.home, odd_group.total, self.price)
        elif self.type == "under":
            return "Total ({} vs {}) U{} ({})".format(event.away, event.home, odd_group.total, self.price)
        return "Unknown"

    def get_multiplier(self):
        multiplier = Decimal(0)
        if self.price > 0:
            multiplier = Decimal(self.price / 100 + 1)
        else:
            multiplier = Decimal(100 / (self.price * -1) + 1)
        return multiplier

    # user type to get event ex. od.h_sprd
    def get_event(self):
        odd_group = getattr(self, self.type)
        return odd_group.event

    def get_odd_group(self):
        return getattr(self, self.type)

    def get_event_status(self):
        event = self.get_event()
        return event.live_status

    def get_event_start_time(self):
        event = self.get_event()
        return event.start_time


class EventManager(models.Manager):
    def get_all_pregame(self):
        return self.get_queryset().filter(live_status=0)


class Event(models.Model):

    LIVE_STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'live'),
        (2, 'complete'),
        (3, 'canceled')
    )

    game_id = models.CharField(primary_key=True, max_length=100)
    sport = models.CharField(max_length=24)
    start_time = models.DateTimeField()
    home = models.CharField(max_length=100)
    away = models.CharField(max_length=100)
    h_score = models.IntegerField(default=0, null=True)
    a_score = models.IntegerField(default=0, null=True)
    live_status = models.IntegerField(choices=LIVE_STATUS_OPTIONS, default=0)
    featured = models.BooleanField(default=False)

    objects = EventManager()

    def __str__(self):
        return "{} @ {}".format(self.away, self.home)

    def get_absolute_url(self):
        return "/sportsbook/{}".format(self.game_id)


class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'sport', 'start_time', 'live_status', 'featured')
    list_filter = ('live_status', 'sport')


class OddsGroup(models.Model):
    ODDS_GROUP_STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'live'),
        (2, 'complete'),
        (3, 'canceled')
    )

    id = models.CharField(primary_key=True, max_length=100)
    type = models.CharField(max_length=24)
    h_score = models.IntegerField(default=0, null=True)
    a_score = models.IntegerField(default=0, null=True)
    h_sprd = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='h_sprd', null=True)
    a_sprd = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='a_sprd', null=True)
    handicap = models.DecimalField(max_digits=7, decimal_places=1)
    h_line = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='h_line', null=True)
    a_line = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='a_line', null=True)
    total = models.DecimalField(max_digits=7, decimal_places=1, null=True)
    over = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='over', null=True)
    under = models.OneToOneField(Odds, on_delete=models.CASCADE, related_name='under', null=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    live_status = models.IntegerField(choices=ODDS_GROUP_STATUS_OPTIONS, default=0)

    def __str__(self):
        return "{} => {}".format(self.event, self.type)

    def final_h_line(self):
        bets = self.betvalue_set.filter(type='h_line')
        home = int(self.h_score)
        away = int(self.a_score)
        if bets:
            for bet in bets:
                if home == away:
                    bet.status = 3
                elif home > away:
                    bet.status = 2
                elif home < away:
                    bet.status = 1
                bet.save()

    def final_a_line(self):
        bets = self.betvalue_set.filter(type='a_line')
        home = int(self.h_score)
        away = int(self.a_score)
        if bets:
            for bet in bets:
                if home == away:
                    bet.status = 3
                elif home > away:
                    bet.status = 1
                elif home < away:
                    bet.status = 2
                bet.save()

    def final_h_spread(self):
        bets = self.betvalue_set.filter(type='h_sprd')
        if bets:
            home = int(self.h_score)
            away = int(self.a_score)
            dif = home - away
            for bet in bets:
                handi = bet.handicap * -1
                if dif == handi:
                    bet.status = 3
                elif dif > handi:
                    bet.status = 2
                elif dif < handi:
                    bet.status = 1
                bet.save()

    def final_a_spread(self):
        bets = self.betvalue_set.filter(type='a_sprd')
        if bets:
            home = int(self.h_score)
            away = int(self.a_score)
            dif = home - away
            for bet in bets:
                handi = bet.handicap * -1
                if dif == handi:
                    bet.status = 3
                elif dif > handi:
                    bet.status = 1
                elif dif < handi:
                    bet.status = 2
                bet.save()

    def final_over(self):
        bets = self.betvalue_set.filter(type='over')
        if bets:
            pts = int(self.h_score) + int(self.a_score)
            for bet in bets:
                total = bet.total
                if total == pts:
                    bet.status = 3
                elif total > pts:
                    bet.status = 1
                elif total < pts:
                    bet.status = 2
                bet.save()

    def final_under(self):
        bets = self.betvalue_set.filter(type='under')
        if bets:
            pts = int(self.h_score) + int(self.a_score)
            for bet in bets:
                total = bet.total
                if total == pts:
                    bet.status = 3
                elif total > pts:
                    bet.status = 2
                elif total < pts:
                    bet.status = 1
                bet.save()

    def push_all_bets(self):
        bets = self.betvalue_set.all()
        for bet in bets:
            bet.status = 3
            bet.save()


    # run all bet updates
    def update_game_bets(self):
        if self.live_status == 2:
            self.final_h_line()
            self.final_a_line()
            self.final_a_spread()
            self.final_h_spread()
            self.final_over()
            self.final_under()
        elif self.live_status == 3:
            self.push_all_bets()


def update_odds(sender, instance, *args, **kwargs):
    instance.update_game_bets()


post_save.connect(update_odds, sender=OddsGroup)


class GameOddsManager(models.Manager):
    def get_full_event_qs(self, event):
        return self.get_queryset().filter(event=event).exclude(h_line=0, total=0, handicap=0)

    def get_first(self, event):
        return self.get_full_event_qs(event).earliest('time')

    def get_last(self, event):
        return self.get_full_event_qs(event).latest('time')

    def get_highest_total(self, event):
        return self.get_queryset().filter(event=event).aggregate(Max('total'))

    def get_lowest_total(self, event):
        return self.get_queryset().filter(event=event).aggregate(Min('total'))


class GameOdds(models.Model):
    handicap = models.DecimalField(max_digits=7, decimal_places=1)
    h_line = models.IntegerField()
    a_line = models.IntegerField()
    total = models.DecimalField(max_digits=7, decimal_places=1, null=True)
    time = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)

    objects = GameOddsManager()

    class Meta:
        verbose_name_plural = "Game Odds"

    def __str__(self):
        return "{} {} => {}".format(self.event, self.handicap, self.time)