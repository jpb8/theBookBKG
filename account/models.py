from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from django.db.models import Sum
from django.contrib import admin


class AccountManager(models.Manager):
    def total_balances(self):
        return self.get_queryset().aggregate(Sum("balance"))


# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    limit = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    customer_id = models.CharField(max_length=120, null=True, blank=True)

    objects = AccountManager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('account:detail', kwargs={'pk': self.pk})

    def check_balance(self, total):
        if total > self.balance:
            return False
        return

    def reward_bet(self, win):
        with transaction.atomic():
            self.balance += win
            self.save()
            print("Paid {}".format(win))


class AccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'balance', 'limit')