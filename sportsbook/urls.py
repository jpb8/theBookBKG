from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'sportsbook'

urlpatterns = [
    url(r'^$', views.sportsbook_home, name='home'),
    url(r'^nfl', views.nfl, name='nfl'),
    url(r'^ncaaf', views.ncaaf, name='ncaaf'),
    url(r'^ncaab', views.ncaab, name='ncaab'),
    url(r'^nhl', views.nhl, name='nhl'),
    url(r'^nba', views.nba, name='nba'),
    url(r'^mma', views.mma, name='mma'),
    url(r'^base', views.base, name='base'),
    url(r'^values', views.event_values, name='event_values'),
    url(r'^event_values_charts', views.BetValuesAjax.as_view(), name='event_values_charts'),
    path('<slug:pk>/', views.EventDetailView.as_view(), name='event-detail'),
]
