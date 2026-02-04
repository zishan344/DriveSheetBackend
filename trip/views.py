from collections import defaultdict
from datetime import date, timedelta
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from trip.models import Trip, RouteStop, DailyLog, LogSegment
from trip.serializers import (
    TripSerializer, RouteStopSerializer, DailyLogSerializer, 
    LogSegmentSerializer, TripMapSerializer, TripLogsSerializer
)
from trip.services.hos_engine import HOSEngine
from trip.services.route_service import get_route
from trip.services.log_generator import generate_daily_logs


# Create your views here.

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    # everyone can acess and read, write update, delete
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # check data is valid or not
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # Route calculation (from pickup to dropoff)
        route = get_route(
            data["pickup_location"],
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

    @action(detail=True, methods=['get'])
    def map(self, request, pk=None):
        """Get map data including route geometry and stops for a trip."""
        trip = self.get_object()
        serializer = TripMapSerializer(trip)
        
        # Add geometry from the route if available (stored in first route stop)
        data = serializer.data
        
        # Optionally fetch fresh geometry if needed
        try:
            route = get_route(trip.pickup_location, trip.drop_location)
            data['geometry'] = route.get('geometry')
        except Exception:
            # If fresh fetch fails, data will just not include live geometry
            pass
        
        return Response(data)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get daily logs with all log segments for a trip."""
        trip = self.get_object()
        serializer = TripLogsSerializer(trip)
        return Response(serializer.data)

