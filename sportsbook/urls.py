from django.conf.urls import url
from . import views

app_name = 'sportsbook'

urlpatterns = [
    url(r'^$', views.sportsbook_home, name='home'),
    url(r'^nfl', views.nfl, name='nfl'),
    url(r'^new', views.new_design, name='new'),
    url(r'^ncaaf', views.ncaaf, name='ncaaf'),
    url(r'^nhl', views.nhl, name='nhl'),
    url(r'^nba', views.nba, name='nba'),
    url(r'^base', views.base, name='base'),
    url(r'^values', views.event_values, name='event_values'),
    url(r'^event_values_charts', views.BetValuesAjax.as_view(), name='event_values_charts'),
]
