from rest_framework.routers import DefaultRouter
from trip.views import TripViewSet
from django.urls import path, include

router = DefaultRouter()

router.register(r'trips', TripViewSet, basename='trip')
""" router.register(r'route-stops', RouteStopViewSet, basename='route-stop')
router.register(r'daily-logs', DailyLogViewSet, basename='daily-log')
router.register(r'log-segments', LogSegmentViewSet, basename='log-segment') """
urlpatterns = [
    path('', include(router.urls)),
]