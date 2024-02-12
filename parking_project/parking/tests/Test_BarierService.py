from django.test import TestCase
from django.contrib.auth import get_user_model
from parking.models import ParkingSpot, ParkingSensor, Barrier, ParkingReservation, Owner
from datetime import timedelta
from django.utils import timezone
from parking.services.BarierService import BarierService

User = get_user_model()

class BarrierOpenTestCase(TestCase):
    def setUp(self):
        # Создание пользователя
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Создание владельца парковочного места
        self.owner = Owner.objects.create(user=self.user, bank_details="Some bank details")

        # Создание парковочного места с указанием владельца
        self.parking_spot = ParkingSpot.objects.create(
            name="Test Parking Spot",
            hourly_rate=10,
            owner=self.owner  # Указываем владельца
        )

        # Создание сенсора для парковочного места
        self.sensor = ParkingSensor.objects.create(
            name="Test Sensor",
            parking_spot=self.parking_spot,
            is_occupied=False
        )

        # Создание барьера, связанного с сенсором и парковочным местом
        self.barrier = Barrier.objects.create(
            name="Test Barrier",
            sensor=self.sensor,
            parking_spot=self.parking_spot,
            is_open=False
        )

        # Создание активного бронирования для пользователя на парковочном месте
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=2)  # Бронирование на 2 часа
        self.reservation = ParkingReservation.objects.create(
            user=self.user,
            parking_spot=self.parking_spot,
            start_time=start_time,
            end_time=end_time,
            status="active"
        )

    def test_open_barrier_with_active_reservation(self):
        # Проверка, что барьер закрыт до выполнения операции
        self.assertFalse(self.barrier.is_open)

        # Вызов функции открытия барьера
        service = BarierService()
        open_result = service.open_barrier(user_id=self.user.id, parking_spot_id=self.parking_spot.id)

        # Обновляем состояние барьера из базы данных
        self.barrier.refresh_from_db()

        # Проверка, что барьер был успешно открыт
        self.assertTrue(self.barrier.is_open)
        self.assertIn("Барьер успешно открыт", open_result)
