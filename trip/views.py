from rest_framework import viewsets
from rest_framework.response import Response
from trip.models import Trip, RouteStop, DailyLog, LogSegment
from trip.serializers import TripSerializer, RouteStopSerializer, DailyLogSerializer, LogSegmentSerializer
from trip.services.hos_engine import HOSEngine
from trip.services.route_service import get_route
from trip.services.log_generator import generate_daily_logs


# Create your views here.

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    def create(self, request, *args, **kwargs):
        trip = Trip.objects.create(
            current_location=request.data["current_location"],
            pickup_location=request.data["pickup_location"],
            dropoff_location=request.data["dropoff_location"],
            cycle_used_hours=request.data["cycle_used_hours"]
        )

        route = get_route(
            request.data["current_location"],
            request.data["dropoff_location"],
        )
        engine = HOSEngine(
            total_distance = route["distance_miles"],
            cycle_used=trip.cycle_used_hours
        )
        stops = engine.simulate()
        logs = generate_daily_logs(stops)
        # save stops
        for s in stops:
            RouteStop.objects.create(
                trip = trip,
                type = s.type,
                duration_minutes = int(s.duration_hrs * 60),
                day_number = s.day
            )
        # save logs
        for day, segments in logs.items():
            daily_log = DailyLog.objects.create(
                trip = trip,
                day_number = day,
            )
            for seg in segments:
                LogSegment.objects.create(
                    daily_log= daily_log,
                    status = seg["status"],
                    start_minutes = seg["start"],
                    end_minutes = seg["end"]
                )
        return Response({"trip_id": str(trip.id)})
    







    
""" class RouteStopViewSet(viewsets.ModelViewSet):
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer
class DailyLogViewSet(viewsets.ModelViewSet):
    queryset = DailyLog.objects.all()
    serializer_class = DailyLogSerializer
class LogSegmentViewSet(viewsets.ModelViewSet):
    queryset = LogSegment.objects.all()
    serializer_class = LogSegmentSerializer
 """
