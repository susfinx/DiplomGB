from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from services.OwnerService import OwnerService
from .models import ParkingSpot, ParkingReservation, Payment, Owner, Address
from .serializers import (
    UserSerializer,
    ParkingSpotSerializer,
    ParkingReservationSerializer,
    PaymentSerializer,
    OpenBarrierRequestSerializer,
)
from .services import BarierService

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny,]
        return super(UserViewSet, self).get_permissions()

class ParkingSpotViewSet(viewsets.ModelViewSet):
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class OpenBarrierView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OpenBarrierRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            parking_spot_id = serializer.validated_data['parking_spot_id']
            service = BarierService()
            result = service.open_barrier(user_id, parking_spot_id)
            if result == "Барьер успешно открыт.":
                return Response({"message": result}, status=status.HTTP_200_OK)
            else:
                return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reserve_parking_spot(request):
    serializer = ParkingReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def cancel_reservation(request, pk):
    try:
        reservation = ParkingReservation.objects.get(pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ParkingReservation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def become_owner(request):
    user_id = request.data.get('user_id')
    # Данные для парковочного места
    name = request.data.get('name')
    hourly_rate = request.data.get('hourly_rate')
    daily_rate = request.data.get('daily_rate')
    monthly_rate = request.data.get('monthly_rate')
    street = request.data.get('street')
    city = request.data.get('city')
    zip_code = request.data.get('zip_code')
    country = request.data.get('country')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    try:
        user = User.objects.get(id=user_id)
        if not Owner.objects.filter(user=user).exists():
            owner = Owner.objects.create(user=user, bank_details="")
            user.is_owner = True
            user.save()

            # Теперь используем сервис для добавления парковочного места
            OwnerService.add_parking_spot(user, name, hourly_rate, daily_rate, monthly_rate, street, city,
                                                zip_code, country, latitude, longitude)

            return Response({"message": "You are now registered as an owner and your parking spot is added."})
        else:
            return Response({"message": "You are already an owner."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
