from django.db import transaction

from .PaymentService import PaymentService
from .exceptions import PaymentFailedException
from ..models import  ParkingReservation,ParkingSpot, Payment, OwnerPayment,ParkingServiceFee
from django.utils import timezone
from datetime import datetime, timedelta


class ReservationService:
    @transaction.atomic
    def reserve_spot(self, user, owner, parking_id, start_time, end_time, tariff):
        try:
            # находим выбранную парковку
            spot = ParkingSpot.objects.get(pk=parking_id)

            # Проверяем доступность парковочного места
            if spot.is_available_hourly or spot.is_available_daily or spot.is_available_monthly:
                # Проверяем, что указанное время бронирования не пересекается с другими бронированиями
                existing_reservations = ParkingReservation.objects.filter(
                    parking_spot=spot,
                    end_time__gte=start_time,
                    start_time__lte=end_time,  # Исправлено на start_time__lte
                )
                if not existing_reservations.exists():
                    # Расчитываем сумму оплаты
                    payment_amount = PaymentService.calculate_payment_amount(tariff, start_time, end_time)

                    # Создаем новое бронирование
                    reservation = ParkingReservation(
                        user=user,
                        parking_spot=spot,
                        start_time=start_time,  # Добавлено
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

                    # Вычисляем сумму комиссии за сервис
                    service_fee = PaymentService.calculate_service_fee(payment_amount)
                    service_fee_entry = ParkingServiceFee(
                        user=user,  # Пользователь, для которого была комиссия
                        owner=owner,  # Владелец (если требуется)
                        reservation=reservation,  # Бронирование (если требуется)
                        amount=service_fee,  # Сумма комиссии
                    )
                    service_fee_entry.save()

                    # Попытка симулированной оплаты, вернет True если прошла успешно, иначе False
                    if PaymentService.simulate_payment(self):
                        # Вычисляем сумму оплаты владельцу с учетом комиссии
                        owner_payment_amount = payment_amount - service_fee

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
                        # Если оплата не прошла, отменяем бронирование
                        reservation.delete()
                        raise PaymentFailedException("Оплата не прошла")

                else:
                    return "Указанное время уже забронировано для этого парковочного места."
            else:
                return "Парковочное место недоступно для бронирования."
        except PaymentFailedException as e:
            return str(e)
        except Exception as e:
            return f"Произошла ошибка при бронировании: {str(e)}"

    @transaction.atomic
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

    def check_availability_hourly(self):
        now = timezone.now()
        # Найдите бронирования с почасовым тарифом, которые завершились
        hourly_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="hourly"
        )

        # Обновите статус парковок, которые освободились после завершения бронирования
        for reservation in hourly_reservations:
            parking_spot = reservation.parking_spot
            if parking_spot.is_available_hourly:
                parking_spot.is_available_hourly = True
                parking_spot.save()

    def check_availability_daily(self):
        now = timezone.now()
        # Найдите бронирования с посуточным тарифом, которые завершились
        daily_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="daily"
        )

        # Обновите статус парковок, которые освободились после завершения бронирования
        for reservation in daily_reservations:
            parking_spot = reservation.parking_spot
            if parking_spot.is_available_daily:
                parking_spot.is_available_daily = True
                parking_spot.save()

    def check_availability_monthly(self):
        now = timezone.now()
        # Найдите бронирования с помесячным тарифом, которые завершились
        monthly_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="monthly"
        )

        # Обновите статус парковок, которые освободились после завершения бронирования
        for reservation in monthly_reservations:
            parking_spot = reservation.parking_spot
            if parking_spot.is_available_monthly:
                parking_spot.is_available_monthly = True
                parking_spot.save()

    def update_parking_spot_availability(self):
        self.check_availability_hourly()
        self.check_availability_daily()
        self.check_availability_monthly()

    def find_expired_reservation_and_occupied_sensor(self):
        try:
            # Получаем текущее время
            current_time = timezone.now()

            # Находим все бронирования, у которых время окончания меньше текущего времени
            expired_reservations = ParkingReservation.objects.filter(
                end_time__lt=current_time,
                status="active"  # Предполагается, что "active" - статус активных бронирований
            )

            # Создаем список для хранения парковок с проблемами
            problem_parking_spots = []

            # Перебираем и проверяем каждое бронирование
            for reservation in expired_reservations:
                spot = reservation.parking_spot
                sensor = spot.sensor

                # Проверяем, что датчик говорит, что парковка занята
                if sensor.is_occupied:
                    problem_parking_spots.append(spot)

            return problem_parking_spots

        except Exception as e:
            # Обработка ошибок, если необходимо
            return []

    def start_hourly_rate(self,parking_spot_id, user_id):
        try:
            # Получаем парковочное место по ID
            parking_spot = ParkingSpot.objects.get(pk=parking_spot_id)

            # Проверяем, доступен ли часовой тариф на парковке
            if not parking_spot.is_hourly_available:
                # Если часовой тариф недоступен, делаем его доступным
                parking_spot.is_hourly_available = True
                parking_spot.save()

            # Создаем бронирование на час и связываем его с пользователем
            current_time = datetime.now()
            end_time = current_time + timedelta(hours=1)

            # Создаем запись о бронировании
            reservation = ParkingReservation.objects.create(
                parking_spot=parking_spot,
                start_time=current_time,
                end_time=end_time,
                user_id=user_id,  # Связываем бронирование с пользователем
                status="active",  # Можете задать другой статус, если необходимо
            )

            reservation.save()

            return "Часовой тариф успешно запущен для парковочного места."
        except ParkingSpot.DoesNotExist:
            return "Парковочное место с указанным ID не найдено."
        except Exception as e:
            return f"Произошла ошибка при запуске часового тарифа: {str(e)}"



