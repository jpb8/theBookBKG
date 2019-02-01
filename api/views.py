from rest_framework import generics
from sportsbook.models import Event
from .serializers import EventSerializer

# Create your views here.


class ListEventsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """

    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.filter(live_status=0)
        sport = self.request.query_params.get('sport', None)
        if sport is not None:
            queryset = queryset.filter(sport=sport)
        return queryset



