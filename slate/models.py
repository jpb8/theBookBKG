from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum, F

from players.models import Player
from teams.models import Team


class LineupManager(models.Manager):
    def under_sal(self, salary, opp1, opp2):
        salary = 50000 - salary
        return self.get_queryset().filter(salary__lte=salary).exclude(
            Q(all_teams__contains=opp1) | Q(all_teams__contains=opp2))

    def group(self, salary, opp1, opp2):
        return self.under_sal(salary, opp1, opp2).values("combo").annotate(count=Count('team1'))


class Lineup(models.Model):
    lu_id = models.CharField(max_length=100, primary_key=True)
    p1 = models.CharField(max_length=124, null=True)
    p2 = models.CharField(max_length=124, null=True)
    c = models.CharField(max_length=124, null=True)
    fB = models.CharField(max_length=124, null=True)
    sB = models.CharField(max_length=124, null=True)
    tB = models.CharField(max_length=124, null=True)
    ss = models.CharField(max_length=124, null=True)
    of1 = models.CharField(max_length=124, null=True)
    of2 = models.CharField(max_length=124, null=True)
    of3 = models.CharField(max_length=124, null=True)
    salary = models.IntegerField(default=0)
    team1 = models.CharField(max_length=10, null=True)
    team2 = models.CharField(max_length=10, null=True)
    all_teams = models.CharField(max_length=124, null=True)
    pts = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    lu_type = models.CharField(max_length=10, null=True)
    combo = models.CharField(max_length=10, null=True)
    dedupe = models.CharField(max_length=124, null=True)

    objects = LineupManager()

    def __str__(self):
        if self.team2:
            return '{} @ {} - {}'.format(self.team1, self.team2, self.lu_type)
        else:
            return '{} - {}'.format(self.team1, self.lu_type)


class ExportManager(models.Manager):
    def users_lus(self, user):
        return self.get_queryset().filter(user=user)

    def group(self, user):
        return self.users_lus(user).values("combo").annotate(lu_count=Count('combo'))

    def pitchers(self, user):
        return self.users_lus(user).values("combo").annotate(lu_count=Count('combo'))

    def teams(self, user):
        t1 = self.users_lus(user).values("team1")
        t2 = self.users_lus(user).values("team2").exclude(team2=None)
        return t1.union(t2).annotate(cnt=Count("team1"))


class ExportLineup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    p1 = models.CharField(max_length=124, null=True)
    p2 = models.CharField(max_length=124, null=True)
    c = models.CharField(max_length=124, null=True)
    fB = models.CharField(max_length=124, null=True)
    sB = models.CharField(max_length=124, null=True)
    tB = models.CharField(max_length=124, null=True)
    ss = models.CharField(max_length=124, null=True)
    of1 = models.CharField(max_length=124, null=True)
    of2 = models.CharField(max_length=124, null=True)
    of3 = models.CharField(max_length=124, null=True)
    salary = models.IntegerField(default=0)
    team1 = models.CharField(max_length=10, null=True)
    team2 = models.CharField(max_length=10, null=True)
    lu_type = models.CharField(max_length=10, null=True)
    combo = models.CharField(max_length=10, null=True)
    dedupe = models.CharField(max_length=122, null=True)

    objects = ExportManager()

    def __str__(self):
        if self.team2:
            return '{} @ {} - {}'.format(self.team1, self.team2, self.lu_type)
        else:
            return '{} - {}'.format(self.team1, self.lu_type)


class Stack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.user, self.team)


class StackPlayerManager(models.Manager):
    def delete_not_in_order(self):
        return self.get_queryset().filter(player__order_pos=0).delete()


class StackPlayer(models.Model):
    stack = models.ForeignKey(Stack, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    order_spot = models.IntegerField(default=0)

    objects = StackPlayerManager()

    def __str__(self):
        return "{}: {}".format(self.player, self.order_spot)


class Punt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dkid = models.IntegerField()
    name_id = models.CharField(max_length=124)
    position = models.CharField(max_length=10)
    salary = models.IntegerField(default=0)

    def __str__(self):
        return "{} {} ${}".format(self.name_id, self.position, self.salary)


class PitcherComboManager(models.Manager):
    def total_percentage(self, user):
        return self.get_queryset().filter(user=user).aggregate(sum=Sum('percent'))

    def import_data(self, user):
        data = []
        combos = self.get_queryset().filter(user=user).order_by("-percent")
        for c in combos:
            data.append({
                "p1": c.p1.name_id,
                "p2": c.p2.name_id,
                "opp1": c.p1.opp,
                "opp2": c.p2.opp,
                "salary": c.p1.salary + c.p2.salary,
                "percent": c.percent
            })
        return data


class PitcherCombo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    p1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p1")
    p2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p2")
    percent = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    objects = PitcherComboManager()

    def __str__(self):
        return "{} {} {}%".format(self.p1.dk_name, self.p2.dk_name, self.percent * 100)
