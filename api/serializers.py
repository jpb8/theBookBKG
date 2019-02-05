from rest_framework import serializers
from sportsbook.models import Event, OddsGroup
from betslip.models import Slip


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OddsGroup
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ("game_id", "sport", 'start_time', 'home', 'away', 'h_score', 'a_score', 'live_status', 'groups')


class LiveEventSerializer(serializers.Serializer):
    sport = serializers.CharField(max_length=25)
    lower_sport = serializers.CharField(max_length=25)