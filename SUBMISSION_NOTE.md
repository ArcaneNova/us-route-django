# US Route Fuel Optimizer - Submission

## Project Link
https://drive.google.com/drive/folders/1dA6AIi8uTtltp_GfF6G1QbzBacuWCNde?usp=sharing

## Quick Overview
Django REST API that finds the cheapest fuel stops for US road trips. Takes start/end locations, returns optimal fuel stops based on real pricing data from 3,780+ stations.

**Key Features:**
- 500-mile vehicle range with 10 MPG fuel economy
- Real-time route optimization using OpenRouteService
- Sub-10ms response time for cached routes
- PostgreSQL database with spatial indexing
- Single API call per request (efficiency optimized)

## Test It Yourself
```bash
# 1. Install & Run
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 2. Test in Postman
POST http://127.0.0.1:8000/api/route/fuel-plan/
Content-Type: application/json

{
  "start": "Chicago, IL",
  "end": "Dallas, TX"
}
```

**Expected Response:** 1 fuel stop, ~$307 total cost, 958 miles

## What's Included
- ✅ Complete working Django 5.2.9 project
- ✅ PostgreSQL cloud database configured
- ✅ 8,151 fuel stations dataset
- ✅ Loom recording guide for demo
- ✅ Performance optimizations (6ms cached)
- ✅ Production-ready code

## Documentation
- `readme.txt` - Original requirements
- `PROJECT_REPORT.md` - Technical details & results
- `LOOM_RECORDING_GUIDE.md` - Step-by-step demo instructions
- `PERFORMANCE_OPTIMIZATIONS.md` - Speed improvements applied

## Tech Stack
Django 5.2.9 | PostgreSQL | Django REST Framework | OpenRouteService API

---

Looking forward to discussing the implementation!
