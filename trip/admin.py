from django.contrib import admin
from .models import Trip, RouteStop,DailyLog,LogSegment
# Register your models here.
admin.site.register(Trip)
admin.site.register(RouteStop)
admin.site.register(DailyLog)
admin.site.register(LogSegment)