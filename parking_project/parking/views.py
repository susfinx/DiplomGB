from django.http import JsonResponse
from django.core.serializers import serialize
from .models import ParkingSpot
from django.shortcuts import render


def parking_spots_geojson(request):
    parking_spots = ParkingSpot.objects.all()
    parking_spots_geojson = serialize('geojson', parking_spots,
                                      geometry_field='location',
                                      fields=('name', 'hourly_rate', 'daily_rate', 'monthly_rate'))
    return JsonResponse(parking_spots_geojson, safe=False)

def show_map(request):
    return render(request, 'parking/map.html')

