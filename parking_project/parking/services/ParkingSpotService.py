from django.utils import timezone
from parking.models import ParkingReservation, ParkingSpot

class ParkingSpotService:

    @staticmethod
    def update_availability(parking_spot_id):
        # Получаем парковочное место по его ID
        parking_spot = ParkingSpot.objects.get(id=parking_spot_id)

        # Получаем текущее время
        now = timezone.now()

        # Проверяем наличие активных бронирований для данного парковочного места
        active_reservations = ParkingReservation.objects.filter(
            parking_spot=parking_spot,
            status="active",
            end_time__gt=now,
        )

        # Устанавливаем доступность в соответствии с текущими бронированиями и настройками владельца
        parking_spot.is_available_hourly = not active_reservations.filter(
            tariff="hourly").exists() if parking_spot.is_available_hourly else False
        parking_spot.is_available_daily = not active_reservations.filter(
            tariff="daily").exists() if parking_spot.is_available_daily else False
        parking_spot.is_available_monthly = not active_reservations.filter(
            tariff="monthly").exists() if parking_spot.is_available_monthly else False

        # Сохраняем обновленное состояние парковочного места
        parking_spot.save()
