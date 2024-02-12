from rest_framework import serializers
from .models import User, Owner, QRCode, Address, ParkingSpot, ParkingSensor, Barrier, ParkingReservation, Payment, OwnerPayment, ParkingServiceFee

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_owner']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['user', 'bank_details']

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ['name', 'image', 'parking_spot']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'zip_code', 'country']

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = ['name', 'hourly_rate', 'daily_rate', 'monthly_rate', 'owner', 'address', 'latitude', 'longitude', 'is_available_hourly', 'is_available_daily', 'is_available_monthly']

class ParkingSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSensor
        fields = ['name', 'is_occupied', 'parking_spot']

class BarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barrier
        fields = ['name', 'is_open', 'sensor', 'parking_spot']

class ParkingReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingReservation
        fields = ['user', 'parking_spot', 'start_time', 'end_time', 'status', 'tariff', 'duration']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['reservation', 'user', 'payment_date', 'amount']

class OwnerPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerPayment
        fields = ['owner', 'user', 'payment', 'amount', 'timestamp']

class ParkingServiceFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingServiceFee
        fields = ['owner', 'reservation', 'amount', 'timestamp']



class OpenBarrierRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="Идентификатор пользователя, запрашивающего открытие барьера")
    parking_spot_id = serializers.IntegerField(help_text="Идентификатор парковочного места, для которого требуется открыть барьер")
