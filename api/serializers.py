from rest_framework import serializers
from api.models import fuelstation

class fuelstationserializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='retail_price', max_digits=10, decimal_places=3, read_only=True)
    
    class Meta:
        model = fuelstation
        fields = ['name', 'city', 'state', 'price', 'latitude', 'longitude']

class routerequestserializer(serializers.Serializer):
    start = serializers.CharField(max_length=255)
    end = serializers.CharField(max_length=255)

class routeresponseserializer(serializers.Serializer):
    distance_miles = serializers.FloatField()
    fuel_stops = fuelstationserializer(many=True)
    total_fuel_cost = serializers.FloatField()
    route_polyline = serializers.CharField()
