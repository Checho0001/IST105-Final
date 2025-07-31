from django.shortcuts import render
from pymongo import MongoClient
from django.utils.timezone import now
import datetime

from .utils import geocode_address, get_route_data, get_weather, get_bc_cities

# MongoDB connection
mongo_client = MongoClient(
    "mongodb://cctb1:cctb2025@<MONGO_EC2_PUBLIC_IP>:27017/cctbdb?authSource=cctbdb"
)
db = mongo_client.cctbdb  
queries_collection = db.queries  

def save_query(start_city, end_city, distance, duration, steps, start_weather, end_weather):
    query_doc = {
        "start_city": start_city,
        "end_city": end_city,
        "timestamp": datetime.datetime.utcnow(),
        "route_summary": {
            "distance_km": distance,
            "duration_min": duration,
        },
        "steps": steps,
        "start_weather": start_weather,
        "end_weather": end_weather,
    }
    queries_collection.insert_one(query_doc)

def home(request):
    context = {}
    context['cities'] = get_bc_cities()

    if request.method == "POST":
        start_city = request.POST.get("start_city")
        end_city = request.POST.get("end_city")

        if not start_city or not end_city:
            context['error'] = "Please select both start and end cities."
            return render(request, "home.html", context)

        start_coords = geocode_address(f"{start_city}, BC, Canada")
        end_coords = geocode_address(f"{end_city}, BC, Canada")

        if not start_coords or not end_coords:
            context['error'] = "Failed to geocode one or both cities."
            return render(request, "home.html", context)

        route_json = get_route_data(start_coords, end_coords)
        if not route_json or 'routes' not in route_json:
            context['error'] = "Could not retrieve route data."
            return render(request, "home.html", context)

        segment = route_json['routes'][0]['segments'][0]
        duration_min = round(segment['duration'] / 60, 2)
        distance_km = round(segment['distance'] / 1000, 2)
        steps = segment.get('steps', [])

        start_weather = get_weather(start_city)
        end_weather = get_weather(end_city)

        now_hour = now().hour
        bad_conditions = ['rain', 'storm', 'snow', 'thunderstorm']
        start_weather_desc = ""
        if start_weather:
            start_weather_desc = start_weather.get('weather', [{}])[0].get('description', '').lower()
        if any(cond in start_weather_desc for cond in bad_conditions) or now_hour < 6 or now_hour > 22:
            advice = "Consider delaying your trip due to bad weather or inconvenient time."
        else:
            advice = "Good time to start your trip!"

        try:
            save_query(start_city, end_city, distance_km, duration_min, steps, start_weather, end_weather)
        except Exception as e:
            context['mongo_error'] = f"Failed to save query: {e}"

        context.update({
            "start_city": start_city,
            "end_city": end_city,
            "duration_min": duration_min,
            "distance_km": distance_km,
            "steps": steps,
            "weather_start": start_weather,
            "weather_end": end_weather,
            "advice": advice,
        })

    return render(request, "home.html", context)

def history(request):
    try:
        saved_queries = list(queries_collection.find().sort("timestamp", -1).limit(50))
    except Exception:
        saved_queries = []
    return render(request, "history.html", {"saved_queries": saved_queries})
