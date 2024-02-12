from celery import Celery
from celery.schedules import crontab
from parking.constants import CLOSE_ALL_BARRIER, UPDATE_AVAILABILITY, CHECK_EXPIRED


# Загрузка конфигурации из настроек Django


# Автоматическое обнаружение и регистрация задач из всех приложений Django


app = Celery('parking_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

CELERY_BEAT_SCHEDULE = {
    'close_barrier_every_5_minutes': {
        'task': 'parking_project.tasks.close_barrier_task',
        'schedule': crontab(minute=CLOSE_ALL_BARRIER),
    },
    'update_parking_availability_every_5_minutes': {
        'task': 'parking_project.tasks.update_parking_availability',
        'schedule': crontab(minute=UPDATE_AVAILABILITY),
    },
    'check_expired_reservations_and_start_hourly_rates': {
        'task': 'parking_project.tasks.check_expired_reservations_and_start_hourly_rates',
        'schedule': crontab(minute=CHECK_EXPIRED),
    },
}
