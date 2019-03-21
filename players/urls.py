from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
    path('upload_players', views.upload_player, name='upload_players'),
    path('available_lineups', views.available_lineups, name='available_lineups'),
    path('stats', views.stats, name='stats'),
]