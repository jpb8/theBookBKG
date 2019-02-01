from rest_framework import serializers
from sportsbook.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("game_id", "sport", 'start_time', 'home', 'away', 'h_score', 'a_score', 'live_status')