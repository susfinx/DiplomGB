from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Объединенный импорт представлений
from parking.views import (
    OpenBarrierView,
    ParkingSpotViewSet,
    reserve_parking_spot,
    cancel_reservation,
    PaymentViewSet,
)

router = DefaultRouter()
router.register(r'parking_spots', ParkingSpotViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('open_barrier/', OpenBarrierView.as_view(), name='open_barrier'),
    path('', include(router.urls)),
    path('reserve_parking_spot/', reserve_parking_spot, name='reserve_parking_spot'),
    path('cancel_reservation/<int:pk>/', cancel_reservation, name='cancel_reservation'),
]
