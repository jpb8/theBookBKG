from django.urls import path
from . import views

app_name = 'slate'

urlpatterns = [
    path("stack_add", views.stack_add, name="stack_add"),
    path("remove", views.remove, name="remove"),
    path("lineups", views.lineups, name="lineups"),
    path("add_lineups", views.add_lineups, name="add_lineups"),
    path("delete_all", views.delete_all, name="delete_all"),
    path("update_orders", views.update_pro_orders, name="update_pro_orders"),
    path("lineup_check", views.lineup_check, name="lineup_check"),
    path("refresh_lus", views.refresh_big_kahuna, name="refresh_lus"),
    path("add_punts", views.add_punts, name="add_punts"),
    path("remove_punts", views.remove_punts, name="remove_punts"),
    path("delete_bad_lines", views.delete_bad_lines, name="delete_bad_lines"),
    path("update_line_lineups", views.update_live_lineups, name="update_live_lineups"),
    path("team_breakdown", views.team_breakdown, name="team_breakdown"),
    path("lineup_builder", views.lineup_builder, name="lineup_builder"),
]