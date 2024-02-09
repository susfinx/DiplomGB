from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import HOURLY_RATE, DAILY_RATE, MONTHLY_RATE
from django.utils import timezone

class User(AbstractUser):
    is_owner = models.BooleanField(default=False,help_text="Указывает, является ли пользователь владельцем парковочного места.")

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='owner_profile')
    bank_details = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class QRCode(models.Model):
    name = models.CharField(max_length=100, blank=True)
    image = models.BinaryField()
    parking_spot = models.ForeignKey('ParkingSpot', on_delete=models.CASCADE, related_name='qr_codes')

    def __str__(self):
        return self.name

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"{self.street}, {self.city}, {self.zip_code}, {self.country}"

class ParkingSpot(models.Model):
    name = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, default=HOURLY_RATE)
    daily_rate = models.DecimalField(max_digits=5, decimal_places=2, default=DAILY_RATE)
    monthly_rate = models.DecimalField(max_digits=5, decimal_places=2, default=MONTHLY_RATE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='parking_spots')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='parking_spots')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_available_hourly = models.BooleanField(default=True)
    is_available_daily = models.BooleanField(default=True)
    is_available_monthly = models.BooleanField(default=True)

    def update_availability(self):
        # Получаем текущее время
        now = timezone.now()

        # Находим все активные бронирования для этого парковочного места
        active_reservations = ParkingReservation.objects.filter(
            parking_spot=self,
            status="active",  # Предполагается, что "active" - статус активных бронирований
            end_time__gt=now,  # Бронирования, которые еще не завершились
        )

        # Обновляем статус доступности парковочного места на основе активных бронирований
        self.is_available_hourly = not active_reservations.filter(tariff="hourly").exists()
        self.is_available_daily = not active_reservations.filter(tariff="daily").exists()
        self.is_available_monthly = not active_reservations.filter(tariff="monthly").exists()
        self.save()

    def __str__(self):
        return self.name

class ParkingSensor(models.Model):
    name = models.CharField(max_length=100)
    is_occupied = models.BooleanField(default=False)
    parking_spot = models.ForeignKey('ParkingSpot', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Barrier(models.Model):
    name = models.CharField(max_length=100)
    is_open = models.BooleanField(default=False)
    opening_delay = models.BooleanField(default=False)  # Поле задержки открытия (булевое значение)
    sensor = models.OneToOneField('ParkingSensor', on_delete=models.CASCADE, related_name='barrier')
    parking_spot = models.ForeignKey('ParkingSpot', on_delete=models.CASCADE, related_name='barriers')

    def __str__(self):
        return self.name

class ParkingReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='reservations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default="active")

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.parking_spot.name} from {self.start_time} to {self.end_time}"

    @property
    def is_active(self):
        return self.status == "active" and self.end_time >= timezone.now()

class Payment(models.Model):
    reservation = models.ForeignKey(ParkingReservation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tariff = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment #{self.id}"

class OwnerPayment(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='owner_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Owner Payment #{self.id}"

class ParkingServiceFee(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='service_fees')
    reservation = models.ForeignKey('ParkingReservation', on_delete=models.CASCADE, related_name='service_fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Service Fee for {self.reservation} - {self.timestamp}"
