import logging
from django.utils import timezone
from datetime import timedelta
from ..constants import BARIER_OPENING_DELAY_MINUTES
from ..models import Barrier, ParkingReservation


class BarierService:

    def open_barrier(self, user_id, parking_spot_id):
        # Найти активные бронирования для пользователя на данном парковочном месте
        reservations = ParkingReservation.objects.filter(
            user_id=user_id,
            parking_spot_id=parking_spot_id,
            end_time__gte=timezone.now(),
            status="active"
        )
        if not reservations.exists():
            return "Нет активных бронирований для данного пользователя на выбранном парковочном месте."

        # Найти барьер, связанный с указанным парковочным местом
        try:
            barrier = Barrier.objects.get(parking_spot_id=parking_spot_id)
        except Barrier.DoesNotExist:
            return "Барьер для данного парковочного места не найден."

        # Проверяем сигнал с датчика, связанного с барьером
        sensor = barrier.sensor
        if sensor.is_occupied:
            return "Место занято. Доступ запрещен."

        # Если место свободно, Логика открытия механизма непосредственно.


        # Создаем время окончания задержки (используя значение из константы)

        barrier.is_open = True  # Отметка об открытии барьера
        barrier.save()

        delay_end_time = timezone.now() + timedelta(minutes=BARIER_OPENING_DELAY_MINUTES)

        from tasks import close_barrier_delayed
        close_barrier_delayed.apply_async(args=[barrier.pk, delay_end_time], eta=delay_end_time)

        return "Барьер успешно открыт."

    def close_barrier(self, barrier_id):
        try:
            barrier = Barrier.objects.get(pk=barrier_id)
            sensor_signal = barrier.sensor

            # Проверяем, активна ли задержка открытия
            if barrier.is_open:
                logging.info(f"Запорный механизм {barrier.name} находится в режиме задержки открытия.")
                return "Запорный механизм находится в режиме задержки открытия."

            # Проверяем сигнал с датчика
            if not sensor_signal.is_occupied:
                # Если датчик сигнализирует, что место свободно, закрываем механизм
                logging.info(f"Запорный механизм {barrier.name} успешно закрыт.")

                # Вызываем переданную функцию close_barrier_delayed_func
                self.close_barrier_mechanism(barrier.pk)

                barrier.is_open = False  # Обновляем статус барьера как закрытый
                barrier.save()
                return "Запорный механизм успешно закрыт."
            else:
                # Если датчик сигнализирует о препятствии
                logging.warning(f"Сигнал с датчика для {barrier.name}: препятствия на парковке")
                return "Невозможно закрыть запорный механизм из-за препятствий."

        except Barrier.DoesNotExist:
            logging.error(f"Барьер с ID {barrier_id} не найден.")
            return f"Барьер с ID {barrier_id} не найден."
        except Exception as e:
            logging.error(f"Произошла ошибка при закрытии запорного механизма: {e}")
            return f"Произошла ошибка при закрытии запорного механизма: {e}"

    def close_barrier_mechanism(self, barrier):
        # Реализация закрытия механизма
        pass

