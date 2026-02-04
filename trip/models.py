import uuid
from django.db import models

# Create your models here.

class Trip(models.Model):
    id  = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    cycle_used_hours = models.FloatField()
    total_distance_miles = models.FloatField(blank=True)
    total_duration_hours = models.FloatField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    
class RouteStop(models.Model):
    
    type_choices = [
        ('DRIVING', 'Driving'),
        ('PICKUP', 'Pickup'),
        ('DROPOFF', 'Dropoff'),
        ('REST', 'Rest'),
        ('FUEL', 'Fuel'),
        ('BREAK', 'Break'),
    ]

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    trip = models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='route_stops')
    type = models.CharField(max_length=10,choices=type_choices)
    location_name = models.CharField(max_length=255,blank=True,null=True)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    duration_minutes = models.IntegerField()
    day_number = models.IntegerField()
    def __str__(self):
        return str(self.id)
    
class DailyLog(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    trip_id = models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='daily_logs')
    day_number = models.IntegerField()
    date = models.DateField()
    total_driving_hours = models.DurationField()
    total_on_duty_hour = models.DurationField()
    total_off_duty_hour = models.DurationField()
    def __str__(self):
        return str(self.id)

class LogSegment(models.Model):
    status_choices =[
        ('OFF','Off Duty'),
        ('SLEEPER','Sleeper Berth'),
        ('DRIVING','Driving'),
        ('ON_DUTY','On Duty'),
    ]

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    daily_log = models.ForeignKey(DailyLog,on_delete=models.CASCADE,related_name='log_segments')
    status = models.CharField(max_length=10,choices=status_choices)
    start_minute = models.IntegerField()
    end_minute = models.IntegerField()