from django.db import models
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from teams.models import Team


# Create your models here.
class PlayerManager(models.Manager):
    def team_lineup(self, team):
        return self.get_queryset().filter(team=team).exclude(lineup_pos=0)

    def all_team_batters(self, team):
        return self.get_queryset().filter(team=team).exclude(pos="P")

    def get_games(self):
        return self.get_queryset().values("game_info").annotate(pcount=Count('dkid'))

    def all_starters(self):
        return self.get_queryset().filter(position="SP", starting=True)


class Player(models.Model):
    dkid = models.IntegerField()
    dk_name = models.CharField(max_length=124)
    rotowire_name = models.CharField(max_length=124)
    name_id = models.CharField(max_length=124)
    position = models.CharField(max_length=10)
    second_pos = models.CharField(max_length=10)
    salary = models.IntegerField(default=0)
    game_info = models.CharField(max_length=124)
    team = models.CharField(max_length=10)
    starting = models.BooleanField(default=False)
    order_pos = models.IntegerField(default=0)
    throws = models.CharField(max_length=5, null=True)

    objects = PlayerManager()

    def __str__(self):
        return "{} {} {}".format(self.dk_name, self.position, self.team)

    @classmethod
    def upload_dk(cls, data):
        teams = []
        games = []
        for col in data:
            positions = col[0].split("/")
            pos_1 = positions[0]
            pos_2 = ""
            if len(positions) == 2:
                pos_2 = positions[1]
            print(col[5])
            t = col[7]
            if t not in teams:
                teams.append(t)
                info = col[6].split(" ")
                g = info[0].split("@")[1], info[0].split("@")[0]
                games.append(g) if g not in games else None
                print(games)
            player, created = cls.objects.update_or_create(
                dkid=col[3],
                dk_name=col[2],
                defaults={
                    "position": pos_1,
                    "second_pos": pos_2,
                    "game_info": col[6],
                    "team": col[7],
                    "salary": col[5]
                }
            )
        Team.update_slate(teams)
        Team.add_opp(games)


class DkGame(models.Model):
    home = models.CharField(max_length=10)
    away = models.CharField(max_length=10)
    sport = models.CharField(max_length=10)
    start_time = models.DateTimeField()

    def __str__(self):
        return "{} @ {} {}".format(self.away, self.home, self.start_time)

    @classmethod
    def upload_dk(cls, games):
        for g in games:
            info = g["game_info"].split(" ")
            _home, _away = info[0].split("@")[1], info[0].split("@")[0]
            naive_start_time = "{} {}".format(info[1], info[2])
            print(naive_start_time)
            print(_away + "@" + _home)


class Pitching(models.Model):
    HANDEDNESS_OPTIONS = (
        (0, 'R'),
        (1, 'L'),
        (2, "A"),
        (3, "S")
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    vs = models.IntegerField(choices=HANDEDNESS_OPTIONS)
    kk_p9 = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    bb_p9 = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    kk_pbb = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    hr_p9 = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    kp = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    avg = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    babip = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    whip = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    era = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    siera = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    def __str__(self):
        return "{} vs {}".format(self.player, self.vs)

    @classmethod
    def upload(cls, data, hand):
        for r in data:
            try:
                player = Player.objects.filter(dk_name=r[0])[:1].get()
                _s, new = cls.objects.update_or_create(player=player,
                                                       vs=hand,
                                                       defaults={
                                                           "kk_p9": Decimal(r[2]),
                                                           "bb_p9": Decimal(r[3]),
                                                           "kk_pbb": Decimal(r[4]),
                                                           "hr_p9": Decimal(r[5]),
                                                           "kp": Decimal(r[6][:-1]),
                                                           "avg": Decimal(r[9]),
                                                           "whip": Decimal(r[10]),
                                                           "babip": Decimal(r[11]),
                                                           "era": Decimal(r[16]),
                                                           "siera": Decimal(r[20]) if 20 in r else 0.00,
                                                       })
                print(player, new)
            except Player.DoesNotExist:
                print("No player")


class Batting(models.Model):
    HANDEDNESS_OPTIONS = (
        (0, 'R'),
        (1, 'L'),
        (2, "A"),
        (3, "S")
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    vs = models.IntegerField(choices=HANDEDNESS_OPTIONS)
    pa = models.IntegerField()
    kp = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    avg = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    slg = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    ops = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    iso = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    woba = models.DecimalField(default=0.00, max_digits=10, decimal_places=3)
    hard_p = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    def __str__(self):
        return "{} vs {}".format(self.player, self.vs)

    @classmethod
    def upload(cls, data, hand):
        for r in data:
            try:
                player = Player.objects.filter(dk_name=r[0])[:1].get()
                _s, new = cls.objects.update_or_create(player=player,
                                                       vs=hand,
                                                       defaults={
                                                           "pa": int(r[2]),
                                                           "kp": Decimal(r[4][:-1]),
                                                           "avg": Decimal(r[6]) if hand == 2 else 0,
                                                           "slg": Decimal(r[8]),
                                                           "ops": Decimal(r[9]),
                                                           "iso": Decimal(r[10]),
                                                           "woba": Decimal(r[18]) if hand == 2 else Decimal(r[15]),
                                                           "hard_p": Decimal(r[20][:-1]) if hand == 2 and len(
                                                               r[20]) != 0 else 0
                                                       })
                print(player, new)
            except Player.DoesNotExist:
                print("No player")

    @classmethod
    def upload_team(cls, data, hand):
        for r in data:
            try:
                team = Team.objects.filter(fg_name=r[0])[:1].get()
                _s, new = cls.objects.update_or_create(team=team,
                                                       vs=hand,
                                                       defaults={
                                                           "pa": int(r[1]),
                                                           "kp": Decimal(r[3][:-1]),
                                                           "slg": Decimal(r[7]),
                                                           "ops": Decimal(r[8]),
                                                           "iso": Decimal(r[9]),
                                                           "woba": Decimal(r[14]),
                                                       })
                print(team, new)
            except Player.DoesNotExist:
                print("No player")
