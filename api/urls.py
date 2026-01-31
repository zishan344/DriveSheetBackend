from rest_framework.routers import DefaultRouter
from trip.views import TripViewSet
from django.urls import path, include

router = DefaultRouter()

router.register(r'trips', TripViewSet, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
]