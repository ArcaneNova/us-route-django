from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import routerequestserializer, routeresponseserializer, fuelstationserializer
from api.services.routing import get_route
from api.services.fuel_optimizer import find_fuel_stops
from django.core.cache import cache
import hashlib

class fuelplanview(APIView):
    
    def post(self, request):
        serializer = routerequestserializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        
        cache_key = f"fuel_plan_{hashlib.md5(f'{start}_{end}'.encode()).hexdigest()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        route_data = get_route(start, end)
        
        if not route_data:
            return Response(
                {'error': 'could not find route'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fuel_stops, total_cost = find_fuel_stops(route_data)
        
        polyline = route_data['geometry'] if isinstance(route_data['geometry'], str) else ''
        
        response_data = {
            'distance_miles': round(route_data['distance_miles'], 2),
            'fuel_stops': fuelstationserializer(fuel_stops, many=True).data,
            'total_fuel_cost': total_cost,
            'route_polyline': polyline
        }
        
        cache.set(cache_key, response_data, timeout=86400)
        
        return Response(response_data)
