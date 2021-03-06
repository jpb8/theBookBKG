from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
    path('upload_players', views.upload_player, name='upload_players'),
    path('available_lineups', views.available_lineups, name='available_lineups'),
    path('stats', views.stats, name='stats'),
    path('starters_order', views.starters_order, name='starters_order'),
    path('stack_builder', views.stack_builder, name='stack_builder'),
    path('', views.index, name='index'),
    path('pitching', views.pitching_stats, name='pitching'),
    path('stacks', views.stacks_stats, name='stacks'),
    path('pstats', views.team_stats, name='pstats'),
    path('player_bats', views.player_bats, name='player_bats'),
    path('pull_projections', views.pull_projections, name='pull_projections'),
    path('stacks_call', views.stacks_call, name='stacks_call'),
    path('pown', views.player_pown, name='pown'),
    path('add_starter', views.add_starter, name='add_starter'),
]
