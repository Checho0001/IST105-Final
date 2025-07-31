import requests

# --- API Keys and Endpoints ---
ORS_DIRECTIONS_API = "https://api.openrouteservice.org/v2/directions/driving-car"
ORS_GEOCODE_API = "https://api.openrouteservice.org/geocode/search?"
ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImE2ZjE4YWExNDQ3MTRjOWViMTcyOTVkNWU3YWU0MTlkIiwiaCI6Im11cm11cjY0In0="

OWM_API = "https://api.openweathermap.org/data/2.5/weather"
OWM_KEY = "a080e7112eb3353ac60d2029e6a67c13"

GEODB_API = "http://geodb-free-service.wirefreethought.com/v1/geo/countries/CA/regions/BC/cities?limit=10"

# --- Functions ---

def get_bc_cities():
    """Fetch 100 cities in British Columbia from GeoDB API."""
    try:
        response = requests.get(GEODB_API)
        response.raise_for_status()
        cities = response.json().get('data', [])
        return sorted([city['name'] for city in cities])
    except Exception as e:
        print(f"GeoDB error: {e}")
        return []

def geocode_address(address):
    """Convert an address into coordinates using OpenRouteService."""
    url = f"{ORS_GEOCODE_API}api_key={ORS_KEY}&text={address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        features = response.json().get("features")
        if features:
            coords = features[0]["geometry"]["coordinates"]
            return coords if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180 else None
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_route_data(start_coords, end_coords):
    """Get route info between two coordinates using OpenRouteService."""
    headers = {
        "Authorization": ORS_KEY,
        "Content-Type": "application/json"
    }
    body = {"coordinates": [start_coords, end_coords]}
    try:
        response = requests.post(ORS_DIRECTIONS_API, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Routing error: {e}")
        return None

def get_weather(city_name):
    """Fetch current weather for a city using OpenWeatherMap."""
    params = {"q": city_name, "appid": OWM_KEY, "units": "metric"}
    try:
        response = requests.get(OWM_API, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Weather error: {e}")
        return None
