from api.models import fuelstation
import math

MAX_RANGE_MILES = 500
MPG = 10
CORRIDOR_MILES = 20

def find_fuel_stops(route_data):
    distance_miles = route_data['distance_miles']
    
    if distance_miles <= MAX_RANGE_MILES:
        return [], 0
    
    route_coords = extract_route_coordinates(route_data)
    
    num_stops = math.ceil(distance_miles / MAX_RANGE_MILES)
    segment_distance = distance_miles / num_stops
    
    fuel_stops = []
    total_cost = 0
    current_distance = 0
    
    for i in range(num_stops - 1):
        target_distance = (i + 1) * segment_distance
        target_point = interpolate_point_at_distance(route_coords, target_distance, distance_miles)
        
        if target_point:
            nearby_stations = get_stations_near_point(target_point, CORRIDOR_MILES)
            
            if nearby_stations:
                cheapest = min(nearby_stations, key=lambda s: s.retail_price)
                fuel_stops.append(cheapest)
                
                gallons_needed = segment_distance / MPG
                total_cost += float(cheapest.retail_price) * gallons_needed
                current_distance = target_distance
    
    remaining_distance = distance_miles - current_distance
    if fuel_stops:
        last_station = fuel_stops[-1]
        gallons_needed = remaining_distance / MPG
        total_cost += float(last_station.retail_price) * gallons_needed
    else:
        total_cost = distance_miles / MPG * 3.5
    
    return fuel_stops, round(total_cost, 2)

def extract_route_coordinates(route_data):
    if isinstance(route_data['geometry'], str):
        from api.services.routing import decode_polyline
        return decode_polyline(route_data['geometry'])
    elif isinstance(route_data['geometry'], dict) and 'coordinates' in route_data['geometry']:
        return route_data['geometry']['coordinates']
    return []

def interpolate_point_at_distance(coords, target_distance, total_distance):
    if not coords or len(coords) < 2:
        return None
    
    ratio = target_distance / total_distance
    index = int(ratio * (len(coords) - 1))
    
    if index >= len(coords) - 1:
        return coords[-1]
    
    return coords[index]

def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 3959 * c

def get_stations_near_point(point, radius_miles):
    lat, lon = point[1], point[0]
    
    lat_range = radius_miles / 69.0
    lon_range = radius_miles / (69.0 * math.cos(math.radians(lat)))
    
    stations = list(fuelstation.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gte=lat - lat_range,
        latitude__lte=lat + lat_range,
        longitude__gte=lon - lon_range,
        longitude__lte=lon + lon_range
    ).only('id', 'name', 'city', 'state', 'retail_price', 'latitude', 'longitude')[:100])
    
    nearby = []
    for station in stations:
        dist = haversine_distance(
            lat, lon,
            float(station.latitude), float(station.longitude)
        )
        
        if dist <= radius_miles:
            nearby.append(station)
            if len(nearby) >= 20:
                break
    
    return nearby

def calculate_total_fuel_cost(distance_miles, fuel_stops):
    if not fuel_stops:
        return distance_miles / MPG * 3.5
    
    total_cost = 0
    segment_distance = distance_miles / len(fuel_stops)
    
    for stop in fuel_stops:
        gallons = segment_distance / MPG
        total_cost += float(stop.retail_price) * gallons
    
    return round(total_cost, 2)
