from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import HOURLY_RATE, DAILY_RATE, MONTHLY_RATE, SERVICE_COMMISSION_PERCENTAGE
from django.utils import timezone

class User(AbstractUser):
    is_owner = models.BooleanField(default=False, help_text="Указывает, является ли пользователь владельцем парковочного места.")

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    bank_details = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"{self.street}, {self.city}, {self.zip_code}, {self.country}"


from django.db import models

class ParkingSpot(models.Model):
    name = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=5, decimal_places=2)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='parking_spots')
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_available_hourly = models.BooleanField(default=True)
    is_available_daily = models.BooleanField(default=True)
    is_available_monthly = models.BooleanField(default=True)

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Owner Payment #{self.id}"