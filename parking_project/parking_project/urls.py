from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    OpenBarrierView,
    ParkingSpotViewSet,
    PaymentViewSet,
    become_owner,
    add_address,
    reserve_parking_spot,
    cancel_reservation,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'parking_spots', ParkingSpotViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('api/open_barrier/', OpenBarrierView.as_view(), name='open_barrier'),
    path('api/', include(router.urls)),
    path('api/reserve_parking_spot/', reserve_parking_spot, name='reserve_parking_spot'),
    path('api/cancel_reservation/<int:pk>/', cancel_reservation, name='cancel_reservation'),
    path('api/become_owner/', become_owner, name='become_owner'),
    path('api/add_address/', add_address, name='add_address'),
]
