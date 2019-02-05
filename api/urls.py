from django.urls import path
from .views import ListEventsView, LiveEventsView


urlpatterns = [
    path('events/', ListEventsView.as_view(), name="events-all"),
    path('sports/', LiveEventsView.as_view(), name="live-events"),
]