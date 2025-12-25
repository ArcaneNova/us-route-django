from django.urls import path
from api.views import fuelplanview

urlpatterns = [
    path('fuel-plan/', fuelplanview.as_view(), name='fuel_plan'),
]
