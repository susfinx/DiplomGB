from django.test import TestCase
from datetime import timedelta, datetime, timezone
from ..services.ReservationService import ReservationService
from ..models import ParkingSpot, ParkingReservation, User, Owner


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

    class ReservationServiceTest(TestCase):
        def test_reserve_spot_success(self):
            # Создаем парковочное место
            spot = ParkingSpot.objects.create()  # Создайте парковочное место с нужными параметрами

            # Создаем экземпляр сервиса бронирования
            service = ReservationService()

            # Задаем значения для теста
            user = "test_user"
            owner = "test_owner"
            parking_id = spot.id
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=1)
            tariff = "hourly"  # Передаем нужный тариф

            # Вызываем метод reserve_spot с заданными параметрами
            result = service.reserve_spot(user, owner, parking_id, start_time, end_time, tariff)

            # Проверяем результат
            self.assertIn("успешно забронировано", result)

    # Добавьте больше тестов для проверки различных сценариев и ошибок
    class CancelReservationTest(TestCase):
        def setUp(self):
            # Создаем парковочное место и бронирование для теста
            self.parking_spot = ParkingSpot.objects.create(name="Test Parking Spot")
            self.user = User.objects.create(username="test_user")
            self.reservation = ParkingReservation.objects.create(
                user=self.user,
                parking_spot=self.parking_spot,
                start_time=timezone.now(),
                end_time=timezone.now() + timedelta(hours=1),
                status="active"
            )

        def test_cancel_reservation_success(self):
            # Создаем экземпляр сервиса бронирования
            reservation_service = ReservationService()

            # Отменяем бронирование
            result = reservation_service.cancel_reservation(self.user, self.reservation.id)

            # Проверяем, что бронирование успешно отменено
            self.assertEqual(result, "Бронирование успешно отменено.")

            # Проверяем, что статус бронирования изменился на "canceled"
            updated_reservation = ParkingReservation.objects.get(id=self.reservation.id)
            self.assertEqual(updated_reservation.status, "canceled")

            # Проверяем, что доступность парковочного места была обновлена
            updated_spot = ParkingSpot.objects.get(id=self.parking_spot.id)
            self.assertTrue(updated_spot.is_available())

        def test_cancel_nonexistent_reservation(self):
            # Создаем экземпляр сервиса бронирования
            reservation_service = ReservationService()

            # Пытаемся отменить несуществующее бронирование
            result = reservation_service.cancel_reservation(self.user, 999)

            # Проверяем, что возвращается соответствующее сообщение об ошибке
            self.assertEqual(result, "Бронирование с указанным идентификатором не найдено.")

        def test_cancel_already_canceled_reservation(self):
            # Устанавливаем статус бронирования в "canceled"
            self.reservation.status = "canceled"
            self.reservation.save()

            # Создаем экземпляр сервиса бронирования
            reservation_service = ReservationService()

            # Пытаемся отменить уже отмененное бронирование
            result = reservation_service.cancel_reservation(self.user, self.reservation.id)

            # Проверяем, что возвращается соответствующее сообщение об ошибке
            self.assertEqual(result,
                             "Невозможно отменить это бронирование, так как оно уже отменено или завершено.")