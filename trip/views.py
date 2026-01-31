from rest_framework import viewsets
from trip.models import Trip, RouteStop, DailyLog, LogSegment
from trip.serializers import TripSerializer, RouteStopSerializer, DailyLogSerializer, LogSegmentSerializer

# Create your views here.

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
class RouteStopViewSet(viewsets.ModelViewSet):
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer
class DailyLogViewSet(viewsets.ModelViewSet):
    queryset = DailyLog.objects.all()
    serializer_class = DailyLogSerializer
class LogSegmentViewSet(viewsets.ModelViewSet):
    queryset = LogSegment.objects.all()
    serializer_class = LogSegmentSerializer

