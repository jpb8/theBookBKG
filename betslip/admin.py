from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Slip)
admin.site.register(PlacedBet, PlacedBetAdmin)
admin.site.register(BetValue)