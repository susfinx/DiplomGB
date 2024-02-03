from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import qrcode
import qrcode.image.pil

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_owner = models.BooleanField(default=False)  # Флаг, указывающий, является ли пользователь владельцем

    def __str__(self):
        return self.username


    def find_address_by_qr_code(self, qr_code):
        # Реализация метода поиска адреса по QR-коду
        # Вы можете выполнить поиск в базе данных или другим способом
        pass

    def find_address_on_map(self, latitude, longitude):
        # Реализация метода поиска адреса на карте
        # Вы можете использовать геокодирование или другие сервисы
        pass

    def reserve_spot(self, spot, start_time, end_time):
        # Реализация метода бронирования парковочного места
        pass

    def view_reservation_history(self):
        # Реализация метода просмотра истории бронирования
        pass

    def cancel_reservation(self, reservation_id):
        # Реализация метода отмены бронирования
        pass

    def become_owner(self):
        self.is_owner = True
        self.save()

    def register(self, username, email, password):
        # Проверка на существующий email
        if User.objects.filter(email=email).exists():
            return "Пользователь с этим email уже зарегистрирован."

        # Регистрация пользователя
        self.username = username
        self.email = email
        self.password = make_password(password)
        self.save()
        return "Регистрация успешно завершена."


    def authenticate(self, password):
        return check_password(password, self.password)





class ParkingSpot(models.Model):
    name = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=5, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parking_spots')
    is_available_hourly = models.BooleanField(default=True)
    is_available_daily = models.BooleanField(default=True)
    is_available_monthly = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        try:
            # текст, включающий имя парковочного места и его ID
            qr_code_text = f"Парковочное место: {self.name}, ID: {self.id}"

            # QR-код из текста
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_text)
            qr.make(fit=True)

            # Генерация изображения QR-кода
            img = qr.make_image(fill_color="black", back_color="white")

            # Сохраните изображение QR-кода, например, в файл
            qr_code_filename = f"qr_code_{self.id}.png"
            img.save(qr_code_filename)

            return qr_code_filename  # Верните имя файла с QR-кодом

        except Exception as e:
            return None  # Если произошла ошибка, верните None или обработайте исключение

    def reserve(self, user_id, start_time, end_time):
        # Реализация метода бронирования парковочного места
        pass


    def update_availability(self):
        # Реализация метода обновления доступности парковочного места
        pass

class Owner(User):
    bank_details = models.CharField(max_length=100)  # Реквизиты для приема платежей

    def __str__(self):
        return self.username

    def add_address(self, address):
        # Реализация метода добавления адреса
        pass

    def set_spot_price(self, spot_id, hourly_rate, daily_rate, monthly_rate):
        # Реализация метода установки цен для парковочных мест
        pass

    def set_spot_availability(self, spot_id, hourly, daily, monthly):
        # Реализация метода установки доступности для парковочных мест
        pass

    def view_reservation_history(self, address):
        # Реализация метода просмотра истории бронирования по адресу
        pass

class ParkingReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    reservation_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()  # Дата и время окончания бронирования
    status = models.CharField(max_length=20, default="active")  # Статус бронирования (например, "active" или "canceled")

    def __str__(self):
        return f"Бронирование {self.parking_spot} для {self.user} с {self.reservation_time} до {self.end_time}"

    # Другие методы управления бронированием, если необходимо

    def open_barrier(self):
        try:
            # Проверить активность бронирования и датчик присутствия автомобиля
            if self.is_active and self.presence_sensor:
                # Активировать механизм открытия запорного устройства
                # Здесь может быть логика для управления открытием запорного механизма
                return "Запорный механизм открыт."
            elif not self.presence_sensor:
                # Если датчик не обнаруживает присутствие автомобиля
                return "Необходимо освободить пространство для открытия запорного механизма."
            else:
                return "Невозможно открыть запорный механизм: неактивное бронирование."
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"