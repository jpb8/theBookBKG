from django.db import models
from django.contrib.auth.models import User

from players.models import Player
from teams.models import Team


class LineupManager(models.Manager):
    def under_sal(self, salary):
        salary = 50000 - salary
        return self.get_queryset().filter(salary__lte=salary)


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
    lu_type = models.CharField(max_length=10, null=True)

    objects = LineupManager()

    def __str__(self):
        if self.team2:
            return '{} @ {} - {}'.format(self.team1, self.team2, self.lu_type)
        else:
            return '{} - {}'.format(self.team1, self.lu_type)


class ExportLineup(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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


class Stack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.user, self.team)


class StackPlayer(models.Model):
    stack = models.ForeignKey(Stack, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    order_spot = models.IntegerField(default=0)

    def __str__(self):
        return "{}: {}".format(self.player, self.order_spot)
