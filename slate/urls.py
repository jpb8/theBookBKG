from django.urls import path
from . import views

app_name = 'slate'

urlpatterns = [
    path("stack_add", views.stack_add, name="stack_add"),
    path("remove", views.remove, name="remove"),
]