
def generate_daily_logs(stops):
    """Convert an iterable of RouteStopDTO or LogSegmentDTO into a dict
    keyed by day: { day: [ {status, start, end}, ... ] }
    Expects `stop` objects to have `day`, `start_minute`, `end_minute`, and
    `type` (or `status`) attributes.
    """
    daily_logs = {}
    for stop in stops:
        day = stop.day
        seg = {
            "status": getattr(stop, "type", getattr(stop, "status", "")),
            "start": stop.start_minute,
            "end": stop.end_minute,
        }
        daily_logs.setdefault(day, []).append(seg)
    return daily_logs
