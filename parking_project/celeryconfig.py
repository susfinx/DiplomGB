from celery import Celery
from celery.schedules import crontab
from parking.constants import CLOSE_ALL_BARRIER, UPDATE_AVAILABLYTI, CHECK_EXPIRED

app = Celery('your_project')

# Настройки брокера (Redis)
app.conf.broker_url = 'redis://localhost:6379/0'  # URL для Redis

# Настройки для хранения результатов задач (Redis)
app.conf.result_backend = 'redis://localhost:6379/1'  # URL для Redis (разный базовый индекс)

# Настройка сериализации данных (JSON - рекомендуется)
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

CELERY_BEAT_SCHEDULE = {
    'close_barrier_every_5_minutes': {
        'task': 'parking_project.tasks.close_barrier_task',  # Укажите здесь полный путь к задаче
        'schedule': crontab(minute=CLOSE_ALL_BARRIER),  # Запускать каждые 5 минут
    },
    'update_parking_availability_every_5_minutes': {
        'task': 'parking_project.tasks.update_parking_availability',  # Укажите полный путь к задаче
        'schedule': crontab(minute=UPDATE_AVAILABLYTI),  # Запускать каждые 5 минут
    },
    'check_expired_reservations_and_start_hourly_rates': {
        'task': 'parking_project.tasks.check_expired_reservations_and_start_hourly_rates',  # Укажите полный путь к задаче
        'schedule': crontab(minute=CHECK_EXPIRED),  # Запускать каждые 15 минут
    },
}
