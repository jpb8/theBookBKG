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
    path("refresh_lus", views.refresh_materialized_bkg, name="refresh_lus"),
]