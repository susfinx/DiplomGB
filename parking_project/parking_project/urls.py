from django.urls import path
from parking.views import parking_spots_geojson, show_map

urlpatterns = [
    path('api/parking-spots/', parking_spots_geojson, name='parking_spots_geojson'),
    path('map/', show_map, name='show_map'),
]
