from dataclasses import dataclass

MAX_DAILY_DRIVE = 11 #hr
MAX_CYCLE_HOURS = 70 
SPEED_MPH = 55  # miles per hour
BREAK_AFTER = 8  # hours

@dataclass
class Stop:
    type: str
    duration: float
    day :int

class HOSEngine:
    def __init__(self,total_distance,cycle_used):
        self.remaining_miles = total_distance
        self.cycle_left = MAX_CYCLE_HOURS - cycle_used
        self.day = 1
    
    def simulate(self):
        stops = []

        while self.remaining_miles > 0 and self.cycle_left > 0:
            daily_drive = min(
                MAX_DAILY_DRIVE,
                self.remaining_miles/SPEED_MPH,
                self.cycle_left
            )
            # 30 min break if driving > 8 hrs
            if daily_drive > BREAK_AFTER:
                stops.append(Stop("BREAK",0.5,self.day))
            stops.append(Stop("DRIVING",daily_drive, self.day))
            miles_driven = daily_drive * SPEED_MPH
            self.remaining_miles -= miles_driven
            self.cycle_left -= daily_drive

            # end of day rest
            stops.append(Stop("SLEEPER",10, self.day))
            self.day += 1
        return stops

        