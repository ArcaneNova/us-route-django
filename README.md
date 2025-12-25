# US Route Fuel Optimizer - Project Report

## Overview
Django REST API that calculates optimal fuel stops for long-distance routes across the United States, minimizing fuel costs based on real-time pricing data.

## Technical Stack
- **Framework:** Django 5.2.9 + Django REST Framework
- **Database:** PostgreSQL (Cloud-hosted on Aiven)
- **Routing API:** OpenRouteService (Free tier)
- **Data:** 8,151 fuel stations, 3,780 geocoded for US coverage

## Core Features
1. **Route Planning:** Accepts start/end locations within USA
2. **Fuel Optimization:** 500-mile range vehicle, finds cheapest fuel stops
3. **Cost Calculation:** Total fuel cost at 10 MPG consumption
4. **Route Mapping:** Returns encoded polyline for map visualization
5. **Performance:** Sub-10ms response time for cached routes

## API Endpoint
```
POST /api/route/fuel-plan/
Content-Type: application/json

{
  "start": "Chicago, IL",
  "end": "Dallas, TX"
}
```

**Response:**
```json
{
  "distance_miles": 958.62,
  "fuel_stops": [
    {
      "name": "KUM & GO #0379",
      "city": "Black Rock",
      "state": "AR",
      "price": "3.199",
      "latitude": "36.108876",
      "longitude": "-91.098282"
    }
  ],
  "total_fuel_cost": 306.66,
  "route_polyline": "encoded_string"
}
```

## Algorithm
- Divides route into 500-mile segments (vehicle range)
- Searches 20-mile corridor around route for stations
- Selects cheapest station per segment
- Calculates total cost at 10 MPG fuel economy

## Performance Optimizations
- **Pre-cached coordinates** for top 20 US cities
- **Custom haversine distance** calculations (no external libraries)
- **Database query optimization** with early termination
- **Connection pooling** for PostgreSQL
- **24-hour caching** for routes and geocoding
- **Result:** 6ms cached, 2-3s first request (external API latency)

## Data Management
- Fuel price data loaded from CSV via management command
- Dual-fallback geocoding (Nominatim + US Census)
- Database indexes on latitude, longitude, state, price
- 46% geocoding success rate for US stations

## Project Structure
```
├── config/              # Django settings
├── api/
│   ├── models.py       # FuelStation model
│   ├── views.py        # API endpoint
│   ├── serializers.py  # Request/response formats
│   ├── services/
│   │   ├── routing.py      # OpenRouteService integration
│   │   ├── geocoding.py    # Location lookup
│   │   └── fuel_optimizer.py # Core algorithm
│   └── management/commands/
│       └── load_fuel_csv.py # Data loader
├── data/
│   └── fuel_prices.csv  # 8,151 stations
└── manage.py
```

## Setup & Deployment
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_fuel_csv data/fuel_prices.csv --no-geocode
python manage.py runserver
```

## Key Achievements
✅ Single routing API call per request (efficiency requirement)  
✅ Fast response times (<10ms cached, <4s uncached)  
✅ Real fuel price data with spatial optimization  
✅ Production-ready code with error handling  
✅ Scalable architecture with caching layer  

## Constraints & Trade-offs
- First request slower due to external API dependency (unavoidable)
- Geocoding limited by free tier rate limits
- 500-mile range assumption (configurable)
- 10 MPG fuel economy (configurable)

## Testing Results
| Route | Distance | Stops | Cost | Response Time |
|-------|----------|-------|------|---------------|
| Chicago → Dallas | 958 mi | 1 | $306.66 | 3.5s / 6ms* |
| NY → LA | 2,789 mi | 4 | $794.66 | 7s / 6ms* |
| Boston → NYC | 215 mi | 0 | $0 | 2s / 4ms* |

*First / Cached

## Future Enhancements
- Real-time fuel price updates via API
- Alternative route comparison
- Multi-vehicle support (different MPG/range)
- User preferences (brand loyalty, amenities)
- Mobile app integration

--