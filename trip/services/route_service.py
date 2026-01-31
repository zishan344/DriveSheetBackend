import requests
import json
from decouple import config
API_KEY = config("OPENROUTESERVICE_API_KEY")


def _geocode_location(query):
    """Geocode a free-form address string using Nominatim (OpenStreetMap).

    Returns a dict with keys 'lat' and 'lon' as strings.
    Raises ValueError if geocoding fails.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "DriveSheetBackend/1.0"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        results = r.json()
    except requests.RequestException as exc:
        raise ValueError(f"Geocoding failed for '{query}': {exc}")

    if not results:
        raise ValueError(f"Could not geocode location: '{query}'")

    first = results[0]
    return {"lat": first.get("lat"), "lon": first.get("lon")}


def _ensure_dict(obj):
    """Ensure the location is a dict containing lat/lon.

    - If obj is a dict, return it.
    - If obj is a JSON string, parse and return dict.
    - If obj is a free-form address string, geocode it and return {'lat', 'lon'}.
    """
    if isinstance(obj, str):
        # try JSON first
        try:
            parsed = json.loads(obj)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # not JSON — fall through to geocoding
            pass

        # treat as free-form address and geocode
        return _geocode_location(obj)

    if isinstance(obj, dict):
        return obj

    raise ValueError("Location must be a JSON object, dict, or address string")


def _get_lat_lon(loc):
    loc = _ensure_dict(loc)
    lat = loc.get("lat") or loc.get("latitude")
    lon = (
        loc.get("lng")
        or loc.get("lon")
        or loc.get("longitude")
        or loc.get("long")
        or loc.get("lang")
    )
    if lat is None or lon is None:
        raise ValueError(
            "Location must contain latitude and longitude (keys: lat/lng or latitude/longitude)"
        )
    return float(lat), float(lon)


def get_route(origin, destination):
    lat_o, lon_o = _get_lat_lon(origin)
    lat_d, lon_d = _get_lat_lon(destination)

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    payload = {"coordinates": [[lon_o, lat_o], [lon_d, lat_d]]}
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    data = res.json()
    summary = data["routes"][0]["summary"]

    return {
        "distance_miles": summary["distance"] / 1609,
        "duration_hours": summary["duration"] / 3600,
        "geometry": data["routes"][0]["geometry"],
    }