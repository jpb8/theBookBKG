from django.contrib import admin
from .models import Event, Odds, OddsGroup


# Register your models here.
admin.site.register(Event)
admin.site.register(Odds)
admin.site.register(OddsGroup)
