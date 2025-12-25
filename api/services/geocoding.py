from geopy.geocoders import Nominatim
from django.core.cache import cache
import hashlib

# some popular us cities geocodes for quick resp 
CITY_COORDS = {
    'chicago, il': (41.8781, -87.6298),
    'dallas, tx': (32.7767, -96.7970),
    'new york, ny': (40.7128, -74.0060),
    'los angeles, ca': (34.0522, -118.2437),
    'boston, ma': (42.3601, -71.0589),
    'houston, tx': (29.7604, -95.3698),
    'phoenix, az': (33.4484, -112.0740),
    'philadelphia, pa': (39.9526, -75.1652),
    'san antonio, tx': (29.4241, -98.4936),
    'san diego, ca': (32.7157, -117.1611),
    'austin, tx': (30.2672, -97.7431),
    'jacksonville, fl': (30.3322, -81.6557),
    'san francisco, ca': (37.7749, -122.4194),
    'columbus, oh': (39.9612, -82.9988),
    'indianapolis, in': (39.7684, -86.1581),
    'seattle, wa': (47.6062, -122.3321),
    'denver, co': (39.7392, -104.9903),
    'washington, dc': (38.9072, -77.0369),
    'nashville, tn': (36.1627, -86.7816),
    'miami, fl': (25.7617, -80.1918),
}

def geocode_location(location):
    location_lower = location.lower().strip()
    
    if location_lower in CITY_COORDS:
        return CITY_COORDS[location_lower]
    
    cache_key = f"geocode_{hashlib.md5(location.encode()).hexdigest()}"
    cached_coords = cache.get(cache_key)
    if cached_coords:
        return cached_coords
    
    geocoder = Nominatim(user_agent="us_route_app")
    try:
        result = geocoder.geocode(f"{location}, USA")
        if result:
            coords = (result.latitude, result.longitude)
            cache.set(cache_key, coords, timeout=86400)
            return coords
    except Exception as e:
        pass
    
    return None
