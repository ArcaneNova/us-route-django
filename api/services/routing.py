import requests
from django.conf import settings
from django.core.cache import cache
import hashlib
import json
from .geocoding import geocode_location

def get_route(start_location, end_location):
    cache_key = f"route_{hashlib.md5(f'{start_location}_{end_location}'.encode()).hexdigest()}"
    cached_route = cache.get(cache_key)
    if cached_route:
        return cached_route
    
    start_coords = geocode_location(start_location)
    end_coords = geocode_location(end_location)
    
    if not start_coords or not end_coords:
        return None
    
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        'Authorization': settings.OPENROUTESERVICE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'coordinates': [
            [start_coords[1], start_coords[0]],
            [end_coords[1], end_coords[0]]
        ],
        'units': 'mi',
        'geometry_simplify': True
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        route_data = {
            'distance_miles': data['routes'][0]['summary']['distance'],
            'duration': data['routes'][0]['summary']['duration'],
            'geometry': data['routes'][0]['geometry'],
            'coordinates': data['routes'][0]['geometry']['coordinates'] if 'coordinates' in data['routes'][0]['geometry'] else [],
            'start_coords': start_coords,
            'end_coords': end_coords
        }
        
        cache.set(cache_key, route_data, timeout=86400)
        return route_data
    
    return None

def decode_polyline(encoded):
    points = []
    index = 0
    length = len(encoded)
    lat = 0
    lng = 0
    
    while index < length:
        b = 0
        shift = 0
        result = 0
        
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat
        
        shift = 0
        result = 0
        
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        
        points.append([lng * 1e-5, lat * 1e-5])
    
    return points
