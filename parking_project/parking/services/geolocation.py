from django.http import JsonResponse
from ..models import ParkingSpot

class GeolocationService:
    @staticmethod
    def add_location_to_parking_spot(parking_spot_id, latitude, longitude):
        """
        Добавляет координаты местоположения к парковочному месту.
        """
        try:
            parking_spot = ParkingSpot.objects.get(id=parking_spot_id)
            parking_spot.latitude = latitude
            parking_spot.longitude = longitude
            parking_spot.save()
            return parking_spot
        except ParkingSpot.DoesNotExist:
            return None

    @staticmethod
    def find_parking_spot_by_coordinates(latitude, longitude):
        """
        Находит парковочное место по заданным координатам.
        """
        # Здесь может быть реализация поиска ближайшего парковочного места
        # к заданным координатам, например, с использованием гео-запросов.
        parking_spots = ParkingSpot.objects.filter(latitude=latitude, longitude=longitude)
        if parking_spots:
            return parking_spots.first()  # Возвращает первое найденное место
        else:
            return None
