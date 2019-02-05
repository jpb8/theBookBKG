from rest_framework import generics
from sportsbook.models import Event
from sportsbook.utls import get_event_qs, get_live_sports
from .serializers import EventSerializer, LiveEventSerializer

# Create your views here.


class ListEventsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """

    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = get_event_qs("MMA", "Game")
        sport = self.request.query_params.get('sport', None)
        if sport is not None:
            queryset = get_event_qs(sport, "Game")
        return queryset


class LiveEventsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """

    serializer_class = LiveEventSerializer

    def get_queryset(self):
        queryset = get_live_sports()
        return queryset



