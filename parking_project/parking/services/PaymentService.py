from ..constants import HOURLY_RATE, DAILY_RATE, MONTHLY_RATE, SERVICE_COMMISSION_PERCENTAGE
from ..models import Payment, OwnerPayment


class PaymentService:
    @staticmethod
    def calculate_payment_amount(tariff, start_time, end_time):
        # Переводим разницу между временем начала и окончания бронирования в часы
        duration_hours = (end_time - start_time).total_seconds() / 3600

        # Определяем стоимость бронирования в зависимости от выбранного тарифа
        if tariff == "hourly":
            hourly_rate = HOURLY_RATE
            total_amount = duration_hours * hourly_rate
        elif tariff == "daily":
            daily_rate = DAILY_RATE
            total_amount = daily_rate
        elif tariff == "monthly":
            monthly_rate = MONTHLY_RATE
            total_amount = monthly_rate
        else:
            # Если выбран неизвестный тариф, вернем 0
            total_amount = 0

        return total_amount

    def get_payment_history(self, user, start_date=None, end_date=None):
        try:
            # Фильтруем записи оплат по пользователю
            payments = Payment.objects.filter(user=user)

            # Дополнительно, если указаны даты начала и окончания периода, фильтруем оплаты по этим датам
            if start_date:
                payments = payments.filter(payment_date__gte=start_date)
            if end_date:
                payments = payments.filter(payment_date__lte=end_date)

            # Формируем список оплат в удобном формате
            payment_history = []
            for payment in payments:
                payment_entry = {
                    'amount': payment.amount,
                    'payment_date': payment.payment_date,
                    'parking_spot': payment.reservation.parking_spot.name,
                    # другие поля
                }
                payment_history.append(payment_entry)

            return payment_history
        except Exception as e:
            return f"Произошла ошибка при получении истории оплат: {str(e)}"

    def get_owner_payment_history(self, owner, start_date=None, end_date=None):
        try:
            # Фильтруем записи платежей по владельцу
            owner_payments = OwnerPayment.objects.filter(owner=owner)

            # Дополнительно, если указаны даты начала и окончания периода, фильтруем платежи по этим датам
            if start_date:
                owner_payments = owner_payments.filter(payment_date__gte=start_date)
            if end_date:
                owner_payments = owner_payments.filter(payment_date__lte=end_date)

            # Формируем список платежей владельца в удобном формате
            owner_payment_history = []
            for owner_payment in owner_payments:
                payment_entry = {
                    'amount': owner_payment.amount,
                    'payment_date': owner_payment.payment_date,
                    'parking_spot': owner_payment.parking_spot.name,
                    # Добавьте другие поля, которые вам нужны
                }
                owner_payment_history.append(payment_entry)

            return owner_payment_history
        except Exception as e:
            return f"Произошла ошибка при получении истории платежей: {str(e)}"


