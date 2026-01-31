
def generate_daily_logs(stops):
    daily_logs = {}
    for stop in stops:
        day = stop.day
        if day not in daily_logs:
            daily_logs[day] = []
            current_minute = 0
        else:
            # TODO: should be understood this context
            current_minute = daily_logs[day][-1]['end']
        
        duration_min = int(stop.duration_hr * 60)

        daily_logs[day].append({
            "status": stop.type,
            "start": current_minute,
            "end": current_minute + duration_min
        })
    return daily_logs
