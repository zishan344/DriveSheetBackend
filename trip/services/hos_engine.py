from dataclasses import dataclass

# Constants
MAX_DAILY_DRIVE_HOURS = 11
MAX_CYCLE_HOURS = 70
SPEED_MPH = 55
BREAK_AFTER_HOURS = 8
PICKUP_DROPOFF_MINUTES = 60
FUEL_INTERVAL_MILES = 1000

MINUTES_PER_HOUR = 60
DAY_MINUTES = 1440


@dataclass
class RouteStopDTO:
    type: str
    day: int
    start_minute: int
    end_minute: int


@dataclass
class LogSegmentDTO:
    status: str
    day: int
    start_minute: int
    end_minute: int


class HOSEngine:
    def __init__(self, total_distance_miles: float, cycle_used_hours: float):
        self.total_distance_miles = total_distance_miles
        self.remaining_miles = total_distance_miles
        self.cycle_left_hours = MAX_CYCLE_HOURS - cycle_used_hours
        self.distance_since_fuel = 0
        self.day = 1
        self._pickup_added = False

        self.route_stops: list[RouteStopDTO] = []
        self.log_segments: list[LogSegmentDTO] = []

    def simulate(self):
        # Pickup will be added after the initial OFF block on day 1 inside
        # `_simulate_day` to avoid overlap with the OFF segment.
        while self.remaining_miles > 0 and self.cycle_left_hours > 0:
            self._simulate_day()
            # Advance to the next day only if there will be another simulated day.
            # This prevents overshooting the day counter so dropoff uses the
            # same day as the last driving/log segments when appropriate.
            if self.remaining_miles > 0 and self.cycle_left_hours > 0:
                self.day += 1
        
        # Add dropoff stop at end
        last_segment = self.log_segments[-1] if self.log_segments else None
        if last_segment:
            dropoff_start = last_segment.end_minute
            if dropoff_start + PICKUP_DROPOFF_MINUTES <= DAY_MINUTES:
                self._add_on_duty("DROPOFF", dropoff_start, dropoff_start + PICKUP_DROPOFF_MINUTES)
            else:
                # Dropoff on next day
                self.day += 1
                self._add_on_duty("DROPOFF", 0, PICKUP_DROPOFF_MINUTES)

        return self.route_stops, self.log_segments

    def _simulate_day(self):
        current_minute = 0
        driving_hours_today = min(
            MAX_DAILY_DRIVE_HOURS,
            self.remaining_miles / SPEED_MPH,
            self.cycle_left_hours
        )

        driving_minutes_today = int(driving_hours_today * MINUTES_PER_HOUR)

        # OFF duty before start (cap to day end)
        off_end = min(current_minute + 60, DAY_MINUTES)
        self._add_log("OFF", current_minute, off_end)
        current_minute = off_end

        # Add pickup on day 1 after OFF (only once)
        if self.day == 1 and not self._pickup_added and current_minute < DAY_MINUTES:
            pickup_end = min(current_minute + PICKUP_DROPOFF_MINUTES, DAY_MINUTES)
            self._add_on_duty("PICKUP", current_minute, pickup_end)
            current_minute = pickup_end
            self._pickup_added = True

        # Driving block(s) with fuel stops
        remaining_drive_minutes = driving_minutes_today
        
        while remaining_drive_minutes > 0 and current_minute < DAY_MINUTES:
            # Check if we need a fuel stop — only add if it fits in the day
            if self.distance_since_fuel >= FUEL_INTERVAL_MILES:
                if current_minute + 30 > DAY_MINUTES:
                    # postpone fuel to next day
                    break
                fuel_end = current_minute + 30
                self._add_on_duty("FUEL", current_minute, fuel_end)
                current_minute = fuel_end
                self.distance_since_fuel = 0

            # Drive until break is needed or day ends, capping to day end
            if remaining_drive_minutes > int(BREAK_AFTER_HOURS * MINUTES_PER_HOUR):
                first_drive = int(BREAK_AFTER_HOURS * MINUTES_PER_HOUR)
                drive_minutes = min(first_drive, DAY_MINUTES - current_minute, remaining_drive_minutes)
                if drive_minutes <= 0:
                    break
                self._add_drive(current_minute, current_minute + drive_minutes)
                miles_this_segment = (drive_minutes / MINUTES_PER_HOUR) * SPEED_MPH
                self.distance_since_fuel += miles_this_segment
                current_minute += drive_minutes
                remaining_drive_minutes -= drive_minutes

                # Break (cap to day)
                if current_minute < DAY_MINUTES:
                    break_end = min(current_minute + 30, DAY_MINUTES)
                    self._add_on_duty("BREAK", current_minute, break_end)
                    current_minute = break_end
            else:
                drive_minutes = min(remaining_drive_minutes, DAY_MINUTES - current_minute)
                if drive_minutes <= 0:
                    break
                self._add_drive(current_minute, current_minute + drive_minutes)
                miles_this_segment = (drive_minutes / MINUTES_PER_HOUR) * SPEED_MPH
                self.distance_since_fuel += miles_this_segment
                current_minute += drive_minutes
                remaining_drive_minutes -= drive_minutes

        # End of day sleeper
        if current_minute < DAY_MINUTES:
            self._add_log("SLEEPER", current_minute, DAY_MINUTES)

        # Update counters
        miles_driven = driving_hours_today * SPEED_MPH
        self.remaining_miles -= miles_driven
        self.cycle_left_hours -= driving_hours_today

    # -------- helpers --------

    def _add_drive(self, start, end):
        self.route_stops.append(
            RouteStopDTO("DRIVING", self.day, start, end)
        )
        self.log_segments.append(
            LogSegmentDTO("DRIVING", self.day, start, end)
        )

    def _add_on_duty(self, stop_type, start, end):
        self.route_stops.append(
            RouteStopDTO(stop_type, self.day, start, end)
        )
        self.log_segments.append(
            LogSegmentDTO("ON_DUTY", self.day, start, end)
        )

    def _add_log(self, status, start, end):
        self.log_segments.append(
            LogSegmentDTO(status, self.day, start, end)
        )
