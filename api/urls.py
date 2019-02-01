from django.urls import path
from .views import ListEventsView


urlpatterns = [
    path('events/', ListEventsView.as_view(), name="events-all")
]