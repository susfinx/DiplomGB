import logging
import sys
sys.path.append('C:\\Users\\sx\\PycharmProjects\\Diplom GB Parking\\parking_project')
from celery import Celery, shared_task
from datetime import datetime
from parking.models import Barrier, ParkingSpot
from parking.services.BarierService import BarierService
from parking.services.ReservationService import ReservationService



app = Celery('your_project')
app.config_from_object('celeryconfig')

# Задача, чтобы менять флаг на is_open на False, по прошествию 10 минут после открытия. для автоматического закрытия.
@app.task
def close_barrier_delayed(barrier_id, delay_end_time):
    try:
        barrier = Barrier.objects.get(pk=barrier_id)

        # Проверяем, не прошло ли уже 10 минут
        if barrier.is_open and delay_end_time <= datetime.now():
            # Если прошло, устанавливаем флаг opening_delay в False
            barrier.is_open = False
            barrier.save()
    except Barrier.DoesNotExist:
        logging.error(f"Barrier with id {barrier_id} does not exist.")

# Задача автоматического закрытия барьера с интервалом
@shared_task
def close_barrier_task():
    barriers = Barrier.objects.all()
    auto_close = BarierService()
    for barrier in barriers:
        auto_close.close_barrier(barrier.pk)  # Используйте barrier.pk для передачи ID барьера

# Задача обновления доступности тарифов
@shared_task
def update_parking_availability():
    update_parking = ReservationService()
    update_parking.update_parking_spot_availability()




