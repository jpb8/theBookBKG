from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Event, EventAdmin)
admin.site.register(Odds)
admin.site.register(OddsGroup, OddsGroupAdmin)
admin.site.register(GameOdds)
