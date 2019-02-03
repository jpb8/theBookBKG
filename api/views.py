from rest_framework import generics
from sportsbook.models import Event
from sportsbook.utls import get_event_qs
from .serializers import EventSerializer

# Create your views here.


class ListEventsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """

    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = get_event_qs("NLF", "Game")
        sport = self.request.query_params.get('sport', None)
        if sport is not None:
            queryset = get_event_qs(sport, "Game")
        return queryset



