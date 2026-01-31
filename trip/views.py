from collections import defaultdict
from datetime import date, timedelta
from rest_framework import status, status, viewsets
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
        data = request.data

        # Route calculation
        route = get_route(
            data["current_location"],
            data["drop_location"]
        )

        # Create Trip
        trip = Trip.objects.create(
            current_location=data["current_location"],
            pickup_location=data["pickup_location"],
            drop_location=data["drop_location"],
            cycle_used_hours=float(data["cycle_used_hours"]),
            total_distance_miles=route["distance_miles"],
            total_duration_hours=route["duration_hours"],
        )

        # Run HOS Engine
        engine = HOSEngine(
            total_distance_miles=trip.total_distance_miles,
            cycle_used_hours=trip.cycle_used_hours,
        )

        route_stops_dto, log_segments_dto = engine.simulate()

        # Persist RouteStops
        for stop in route_stops_dto:
            RouteStop.objects.create(
                trip=trip,
                type=stop.type,
                start_time=stop.start_minute,
                end_time=stop.end_minute,
                duration_minutes=stop.end_minute - stop.start_minute,
                day_number=stop.day,
            )

        #  Group LogSegments by day
        logs_by_day = defaultdict(list)
        for seg in log_segments_dto:
            logs_by_day[seg.day].append(seg)

        # Persist DailyLogs + LogSegments
        start_date = date.today()

        for day, segments in logs_by_day.items():
            driving_minutes = sum(
                s.end_minute - s.start_minute
                for s in segments if s.status == "DRIVING"
            )
            on_duty_minutes = sum(
                s.end_minute - s.start_minute
                for s in segments if s.status == "ON_DUTY"
            )
            off_duty_minutes = sum(
                s.end_minute - s.start_minute
                for s in segments if s.status in ("OFF", "SLEEPER")
            )

            daily_log = DailyLog.objects.create(
                trip_id=trip,
                day_number=day,
                date=start_date + timedelta(days=day - 1),
                total_driving_hours=timedelta(minutes=driving_minutes),
                total_on_duty_hour=timedelta(minutes=on_duty_minutes),
                total_off_duty_hour=timedelta(minutes=off_duty_minutes),
            )

            for seg in segments:
                LogSegment.objects.create(
                    daily_log=daily_log,
                    status=seg.status,
                    start_minute=seg.start_minute,
                    end_minute=seg.end_minute,
                )

        # Response
        return Response(
            {
                "trip_id": str(trip.id),
                "total_days": len(logs_by_day),
                "total_distance_miles": trip.total_distance_miles,
            },
            status=status.HTTP_201_CREATED,
        )






    
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
