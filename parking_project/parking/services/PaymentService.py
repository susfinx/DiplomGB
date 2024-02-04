from datetime import timedelta


class PaymentService:
    # Цены по умолчанию
    HOURLY_RATE_DEFAULT = 10
    DAILY_RATE_DEFAULT = 80
    MONTHLY_RATE_DEFAULT = 1000

    @staticmethod
    def calculate_payment_amount(tariff, start_time, end_time):
        # Переводим разницу между временем начала и окончания бронирования в часы
        duration_hours = (end_time - start_time).total_seconds() / 3600

        # Определяем стоимость бронирования в зависимости от выбранного тарифа
        if tariff == "hourly":
            hourly_rate = PaymentService.HOURLY_RATE_DEFAULT
            total_amount = duration_hours * hourly_rate
        elif tariff == "daily":
            daily_rate = PaymentService.DAILY_RATE_DEFAULT
            total_amount = daily_rate
        elif tariff == "monthly":
            monthly_rate = PaymentService.MONTHLY_RATE_DEFAULT
            total_amount = monthly_rate
        else:
            # Если выбран неизвестный тариф, вернем 0
            total_amount = 0

        return total_amount

