from dataclasses import dataclass

# Constants
MAX_DAILY_DRIVE_HOURS = 11
MAX_CYCLE_HOURS = 70
SPEED_MPH = 55
BREAK_AFTER_HOURS = 8

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
        self.remaining_miles = total_distance_miles
        self.cycle_left_hours = MAX_CYCLE_HOURS - cycle_used_hours
        self.day = 1

        self.route_stops: list[RouteStopDTO] = []
        self.log_segments: list[LogSegmentDTO] = []

    def simulate(self):
        while self.remaining_miles > 0 and self.cycle_left_hours > 0:
            self._simulate_day()
            self.day += 1

        return self.route_stops, self.log_segments

    def _simulate_day(self):
        current_minute = 0
        driving_hours_today = min(
            MAX_DAILY_DRIVE_HOURS,
            self.remaining_miles / SPEED_MPH,
            self.cycle_left_hours
        )

        driving_minutes_today = int(driving_hours_today * MINUTES_PER_HOUR)

        # OFF duty before start
        self._add_log("OFF", current_minute, current_minute + 60)
        current_minute += 60

        # Driving block(s)
        if driving_hours_today > BREAK_AFTER_HOURS:
            first_drive = int(BREAK_AFTER_HOURS * MINUTES_PER_HOUR)

            self._add_drive(current_minute, current_minute + first_drive)
            current_minute += first_drive

            # Break
            self._add_on_duty("BREAK", current_minute, current_minute + 30)
            current_minute += 30

            remaining_drive = driving_minutes_today - first_drive
            self._add_drive(current_minute, current_minute + remaining_drive)
            current_minute += remaining_drive
        else:
            self._add_drive(current_minute, current_minute + driving_minutes_today)
            current_minute += driving_minutes_today

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
