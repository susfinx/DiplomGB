from django.test import TestCase
from django.contrib.auth import get_user_model
from parking.models import ParkingSpot, Owner
from parking.services.ParkingSpotService import ParkingSpotService

User = get_user_model()
class ParkingSpotTest(TestCase):
    def setUp(self):
        # Здесь создаем тестового пользователя и владельца парковки для использования в тесте
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_owner = Owner.objects.create(user=test_user, bank_details='Test Bank Details')

        ParkingSpot.objects.create(
            name='Test Parking Spot',
            hourly_rate=10.0,
            daily_rate=50.0,
            monthly_rate=500.0,
            owner=test_owner
        )

    def test_parking_spot_creation(self):
        spot = ParkingSpot.objects.get(name='Test Parking Spot')
        self.assertEqual(spot.hourly_rate, 10.0)
        self.assertEqual(spot.daily_rate, 50.0)
        self.assertEqual(spot.monthly_rate, 500.0)
        self.assertTrue(spot.is_available_hourly)
        self.assertTrue(spot.is_available_daily)
        self.assertTrue(spot.is_available_monthly)
        self.assertEqual(str(spot), 'Test Parking Spot')

    def test_update_availability_with_no_reservations(self):
        # Создаем экземпляр ParkingSpot без бронирований
        user = User.objects.create(username='test_user')
        owner = Owner.objects.create(user=user)
        spot = ParkingSpot.objects.create(name="Test Spot", owner=owner)
        spotService = ParkingSpotService()
        spotService.update_availability(parking_spot_id=spot.id)
        # Проверяем, что все тарифы доступны
        self.assertTrue(spot.is_available_hourly)
        self.assertTrue(spot.is_available_daily)
        self.assertTrue(spot.is_available_monthly)
