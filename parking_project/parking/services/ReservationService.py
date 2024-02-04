from . import PaymentService
from ..models import ParkingSpot, ParkingReservation, Payment
from django.utils import timezone
from datetime import datetime
from ..models import Payment


class ReservationService:
    def reserve_spot(self, user, spot, start_time, end_time, tariff):
        try:
            # Расчитываем сумму оплаты
            payment_amount = PaymentService.calculate_payment_amount(tariff, start_time, end_time)

            # Проверяем доступность парковочного места
            if spot.is_available_hourly or spot.is_available_daily or spot.is_available_monthly:
                # Проверяем, что указанное время бронирования не пересекается с другими бронированиями
                existing_reservations = ParkingReservation.objects.filter(
                    parking_spot=spot,
                    end_time__gte=start_time,
                    reservation_time__lte=end_time,
                )
                if not existing_reservations.exists():
                    # Создаем новое бронирование
                    reservation = ParkingReservation(
                        user=user,
                        parking_spot=spot,
                        end_time=end_time,
                    )
                    reservation.save()

                    # Обновляем доступность парковочного места
                    spot.update_availability()

                    # Создаем запись об оплате
                    payment = Payment(
                        reservation=reservation,
                        user=user,
                        amount=payment_amount,
                        tariff=tariff,
                        timestamp=datetime.now(),  # Добавляем текущую дату и время оплаты
                    )
                    payment.save()

                    # Вычисляем сумму оплаты владельцу с учетом комиссии
                    owner_payment_amount = PaymentService.calculate_owner_payment(payment_amount)

                    # Отправляем оплату владельцу
                    owner_payment = OwnerPayment(
                        owner=spot.owner,
                        user=user,
                        payment=payment,
                        amount=owner_payment_amount,
                    )
                    owner_payment.save()

                    return "Парковочное место успешно забронировано."
                else:
                    return "Указанное время уже забронировано для этого парковочного места."
            else:
                return "Парковочное место недоступно для бронирования."
        except Exception as e:
            return f"Произошла ошибка при бронировании: {str(e)}"


    def view_reservation_history(self, user):
        try:
            # Получить историю бронирований пользователя
            reservations = ParkingReservation.objects.filter(user=user)

            # Можете здесь произвести необходимую обработку и форматирование истории бронирований

            return reservations  # Вернуть историю бронирований пользователя
        except Exception as e:
            return f"Произошла ошибка при получении истории бронирований: {str(e)}"

    def cancel_reservation(self, user, reservation_id):
        try:
            # Найти бронирование по идентификатору и проверить, принадлежит ли оно данному пользователю
            reservation = ParkingReservation.objects.get(id=reservation_id, user=user)

            if reservation.status == "active":
                # Если бронирование активно, отменить его
                reservation.status = "canceled"
                reservation.save()

                # Обновить доступность парковочного места
                reservation.parking_spot.update_availability()

                return "Бронирование успешно отменено."
            else:
                return "Невозможно отменить это бронирование, так как оно уже отменено или завершено."
        except ParkingReservation.DoesNotExist:
            return "Бронирование с указанным идентификатором не найдено."
        except Exception as e:
            return f"Произошла ошибка при отмене бронирования: {str(e)}"

    def update_availability(self):
        try:
            # Получаем все активные бронирования
            active_reservations = ParkingReservation.objects.filter(
                status="active",
                end_time__gte=timezone.now(),
            )

            # Получаем все парковочные места
            parking_spots = ParkingSpot.objects.all()

            # Сначала устанавливаем все места как доступные
            for spot in parking_spots:
                spot.is_available_hourly = True
                spot.is_available_daily = True
                spot.is_available_monthly = True
                spot.save()

            # Затем перебираем активные бронирования и обновляем доступность мест
            for reservation in active_reservations:
                spot = reservation.parking_spot

                # Для бронирования на час
                if reservation.end_time - timezone.now() <= timezone.timedelta(hours=1):
                    spot.is_available_hourly = False

                # Для бронирования на день
                if reservation.end_time - timezone.now() <= timezone.timedelta(days=1):
                    spot.is_available_daily = False

                # Для бронирования на месяц
                if reservation.end_time - timezone.now() <= timezone.timedelta(days=30):
                    spot.is_available_monthly = False

                spot.save()

            return "Доступность парковочных мест успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении доступности парковочных мест: {str(e)}"