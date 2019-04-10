from django.db import models


class TeamManager(models.Manager):
    def on_slate(self):
        return self.get_queryset().filter(on_slate=True)


# Create your models here.
class Team(models.Model):
    dk_name = models.CharField(max_length=10, primary_key=True)
    fg_name = models.CharField(max_length=24, null=True)
    rw_name = models.CharField(max_length=24, null=True)
    league = models.CharField(max_length=10, null=True)
    opp = models.CharField(max_length=10, null=True)
    home = models.BooleanField(default=False)
    on_slate = models.BooleanField(default=False)

    objects = TeamManager()

    def __str__(self):
        return self.dk_name

    @classmethod
    def update_slate(cls, teams):
        cls.objects.all().update(on_slate=False)
        cls.objects.filter(dk_name__in=teams).update(on_slate=True)

    @classmethod
    def add_opp(cls, games):
        cls.objects.all().update(opp="", home=False)
        for g in games:
            home, away = g
            cls.objects.filter(dk_name=home).update(opp=away, home=True)
            cls.objects.filter(dk_name=away).update(opp=home)


class OrdersManager(models.Manager):
    def projected(self, team, game_type):
        return self.get_queryset().filter(game_type=game_type, team__dk_name=team)


class DefaultOrders(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="orders")
    rw_name = models.CharField(max_length=124, null=True)
    game_type = models.CharField(max_length=10, null=True)
    order = models.IntegerField(default=0)

    objects = OrdersManager()

    def __str__(self):
        return "{} {} Bats:{} {}".format(self.rw_name, self.team, self.order, self.game_type)


class ParkFactor(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="factor")
    runs = models.DecimalField(default=1, max_digits=10, decimal_places=3)
    hr = models.DecimalField(default=1, max_digits=10, decimal_places=3)
    h = models.DecimalField(default=1, max_digits=10, decimal_places=3)
    double = models.DecimalField(default=1, max_digits=10, decimal_places=3)
    triple = models.DecimalField(default=1, max_digits=10, decimal_places=3)
    bb = models.DecimalField(default=1, max_digits=10, decimal_places=3)

    def __str__(self):
        return "{} factor: {}".format(self.team, self.runs)
