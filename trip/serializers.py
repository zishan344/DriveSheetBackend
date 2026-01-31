from rest_framework import serializers
from trip.models import Trip, RouteStop, DailyLog, LogSegment

class LogSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSegment
        fields = ['id', 'status', 'start_minute', 'end_minute']

class DailyLogSerializer(serializers.ModelSerializer):
    log_segments = LogSegmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = DailyLog
        fields = ['id', 'day_number', 'date', 'total_driving_hours', 'total_on_duty_hour', 'total_off_duty_hour', 'log_segments']

class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = ['id', 'type', 'start_time', 'end_time', 'duration_minutes', 'day_number', 'location_name']

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

class TripMapSerializer(serializers.ModelSerializer):
    route_stops = RouteStopSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = ['id', 'pickup_location', 'drop_location', 'total_distance_miles', 'total_duration_hours', 'route_stops']

class TripLogsSerializer(serializers.ModelSerializer):
    daily_logs = DailyLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = ['id', 'total_distance_miles', 'total_duration_hours', 'daily_logs']

