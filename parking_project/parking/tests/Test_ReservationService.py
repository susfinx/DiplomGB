from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from parking.models import ParkingSpot, ParkingReservation, Owner
from parking.services.ReservationService import ReservationService

User = get_user_model()

class ReservationServiceTest(TestCase):
    def setUp(self):
        # Создание тестовых данных для бронирования
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.owner = Owner.objects.create(user=self.user, bank_details='Test Bank Details')
        self.spot = ParkingSpot.objects.create(
            name='Test Parking Spot',
            hourly_rate=10.0,
            daily_rate=50.0,
            monthly_rate=500.0,
            owner=self.owner
        )
        self.service = ReservationService()

    def test_reserve_spot_success(self):
        # Тест на успешное создание бронирования
        start_time = timezone.now()
        result = self.service.reserve_spot(self.user, self.owner, self.spot.id, "hourly",1)
        self.assertIn("Парковочное место успешно забронировано", result)

    def test_cancel_reservation_success(self):
        # Подготовка данных для теста отмены бронирования
        start_time = timezone.now() - timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        reservation = ParkingReservation.objects.create(
            user=self.user,
            parking_spot=self.spot,
            start_time=start_time,
            end_time=end_time,
            status='active'
        )

        # Тест на успешную отмену бронирования
        result = self.service.cancel_reservation(self.user.id, reservation.id)
        reservation.refresh_from_db()  # Обновляем информацию о бронировании из БД

        self.assertIn("Бронирование успешно отменено", result)
        self.assertEqual(reservation.status, "cancelled")
