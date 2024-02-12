# rates
HOURLY_RATE = 10.0
DAILY_RATE = 50.0
MONTHLY_RATE = 500.0

# Комиссия сервиса
SERVICE_COMMISSION_PERCENTAGE = 10.0

# Задержка флага барьера при открытии
BARIER_OPENING_DELAY_MINUTES = 10

#авто закрытие всех бариеров
CLOSE_ALL_BARRIER = '*/5'

#Статусы бронирований
STATUS_CHOICES = [
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]
# Статусы Бронирования
TARIFF_CHOICES = [
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('monthly', 'Monthly'),
]

# Обновление доступности парковки
UPDATE_AVAILABILITY = '*/5'

CHECK_EXPIRED = '*/15'


