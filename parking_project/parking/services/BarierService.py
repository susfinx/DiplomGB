import logging

class BarierService:
    def open_barrier(self, user, sensor_signal):
        try:
            # Проверяем, забронировал ли пользователь парковку
            if not user.has_reserved_parking():
                logging.info("Попытка открыть запорный механизм без бронирования")
                return "Для открытия запорного механизма необходимо забронировать парковку."

            # Проверяем сигнал с датчика
            if not sensor_signal.all_clear():
                logging.warning("Сигнал с датчика: препятствия на парковке")
                return "Датчик сигнализирует, что необходимо освободить пространство для открытия запорного механизма."

            # Если оба условия выполняются, открываем запорный механизм
            barrier_status = self.open_barrier_mechanism()

            if barrier_status:
                logging.info("Запорный механизм успешно открыт.")
                return "Запорный механизм успешно открыт."
            else:
                logging.error("Не удалось открыть запорный механизм.")
                return "Не удалось открыть запорный механизм."

        except Exception as e:
            logging.error(f"Произошла ошибка при открытии запорного механизма: {str(e)}")
            return f"Произошла ошибка при открытии запорного механизма: {str(e)}"


    def close_barrier(self, sensor_signal):
        try:
            # Проверяем сигнал с датчика
            if sensor_signal.all_clear():
                # Если датчик сигнализирует, что ничего не мешает, закрываем механизм
                logging.info("Запорный механизм успешно закрыт.")
                self.close_barrier_mechanism()
                return "Запорный механизм успешно закрыт."

            # Если датчик не позволяет закрыть механизм из-за препятствий
            logging.warning("Сигнал с датчика: препятствия на парковке")
            return "Невозможно закрыть запорный механизм из-за препятствий."

        except Exception as e:
            logging.error(f"Произошла ошибка при закрытии запорного механизма: {str(e)}")
            return f"Произошла ошибка при закрытии запорного механизма: {str(e)}"

    def close_barrier_mechanism(self):
        # Реализация закрытия механизма
        pass
