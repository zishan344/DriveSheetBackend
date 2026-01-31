
import requests
from decouple import config
API_KEY = config("OPENROUTESERVICE_API_KEY")

def get_route(origin, destination):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    payload = {
        "coordinates":[
            [origin["lang"], origin["lat"]],
            [destination["lang"], destination["lat"]]
        ]
    }
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    res = requests.post(url, json=payload,headers=headers)
    data = res.json()
    summary = data["routes"][0]["summary"]

    return {
        "distance_miles": summary["distance"]/1609
        ,"duration_hours": summary["duration"]/3600,
        "geometry": data["routes"][0]["geometry"]
    }