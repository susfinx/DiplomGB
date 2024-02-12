from rest_framework.views import APIView
from .serializers import OpenBarrierRequestSerializer
from .services import BarierService  # Убедитесь, что BarierService правильно импортирован
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ParkingSpot, ParkingReservation, Payment
from .serializers import ParkingSpotSerializer, ParkingReservationSerializer, PaymentSerializer


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

class ParkingSpotViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows parking spots to be viewed or edited.
    """
    queryset = ParkingSpot.objects.all()
    serializer_class = ParkingSpotSerializer


@api_view(['POST'])
def reserve_parking_spot(request):
    """
    API endpoint for reserving a parking spot.
    """
    serializer = ParkingReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cancel_reservation(request, pk):
    """
    API endpoint for canceling a parking reservation.
    """
    try:
        reservation = ParkingReservation.objects.get(pk=pk)
    except ParkingReservation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    reservation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
