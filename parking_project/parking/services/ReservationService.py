from django.db import transaction
from dateutil.relativedelta import relativedelta
from .ParkingSpotService import ParkingSpotService
from .PaymentService import PaymentService
from .exceptions import PaymentFailedException
from ..models import ParkingReservation, ParkingSpot, Payment, OwnerPayment, ParkingServiceFee
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal


class ReservationService:
    @transaction.atomic
    def reserve_spot(self, user, owner, parking_id, tariff, duration):

        start_time, end_time = self.calculate_end_time(duration, tariff)

        try:
            spot = ParkingSpot.objects.get(pk=parking_id)

            # Проверка доступности парковочного места в зависимости от тарифа
            if getattr(spot, f'is_available_{tariff}', False):
                # Проверяем, что указанное время бронирования не пересекается с другими бронированиями
                if not ParkingReservation.objects.filter(parking_spot=spot, end_time__gte=start_time,
                                                         start_time__lte=end_time).exists():
                    # Расчет суммы оплаты
                    payment_amount = PaymentService.calculate_payment_amount(tariff, start_time, end_time)

                    # Создание нового бронирования с указанием тарифа
                    reservation = ParkingReservation.objects.create(
                        user=user,
                        parking_spot=spot,
                        start_time=start_time,
                        end_time=end_time,
                        status='active',  # Установка статуса бронирования
                        tariff=tariff
                    )

                    # Обновление доступности парковочного места
                    ParkingSpotService.update_availability(parking_spot_id=spot.id)

                    # Создание записи об оплате
                    payment = Payment.objects.create(
                        reservation=reservation,
                        user=user,
                        amount=payment_amount,
                        payment_date=timezone.now(),
                    )

                    # Вычисление суммы комиссии за сервис
                    service_fee = PaymentService.calculate_service_fee(total_amount=Decimal(payment_amount))
                    owner = spot.owner
                    ParkingServiceFee.objects.create(
                        owner=owner,
                        reservation=reservation,
                        amount=service_fee,
                    )

                    # Попытка имитации оплаты
                    if PaymentService.simulate_payment():
                        owner_payment_amount = Decimal(payment_amount) - service_fee

                        OwnerPayment.objects.create(
                            owner=spot.owner,
                            user=user,
                            payment=payment,
                            amount=owner_payment_amount,
                        )

                        return "Парковочное место успешно забронировано"
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

    @staticmethod
    def calculate_end_time(duration, tariff):
        current_time = timezone.now()
        if tariff == "hourly":
            end_time = current_time + timedelta(hours=duration)
        elif tariff == "daily":
            end_time = current_time + timedelta(days=duration)
        elif tariff == "monthly":
            end_time = current_time + relativedelta(months=duration)
        else:
            # Если тариф неизвестен, можно выбрасывать исключение или возвращать None
            raise ValueError("Unknown tariff")

        return current_time, end_time

    def cancel_reservation(self, user, reservation_id):
        try:
            # Найти бронирование по идентификатору и проверить, принадлежит ли оно данному пользователю
            reservation = ParkingReservation.objects.get(id=reservation_id, user=user)

            if reservation.status == "active":
                # Если бронирование активно, отменить его
                reservation.status = "cancelled"
                reservation.save()

                # Обновить доступность парковочного места
                ParkingSpotService.update_availability(parking_spot_id=reservation.parking_spot.id)

                return "Бронирование успешно отменено."
            else:
                return "Невозможно отменить это бронирование, так как оно уже отменено или завершено."
        except ParkingReservation.DoesNotExist:
            return "Бронирование с указанным идентификатором не найдено."
        except Exception as e:
            return f"Произошла ошибка при отмене бронирования: {str(e)}"

    def update_parking_spot_availability(self):
        problem_parking_spots = []
        self.check_availability_hourly(problem_parking_spots)
        self.check_availability_daily(problem_parking_spots)
        self.check_availability_monthly(problem_parking_spots)
        return problem_parking_spots

    def check_availability_hourly(self, problem_parking_spots):
        now = timezone.now()
        hourly_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="hourly"
        )
        for reservation in hourly_reservations:
            parking_spot = reservation.parking_spot
            sensor = parking_spot.sensor
            if sensor.is_occupied:
                problem_parking_spots.append(parking_spot)
            reservation.status = "expired"
            reservation.save()

    def check_availability_daily(self, problem_parking_spots):
        now = timezone.now()
        daily_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="daily"
        )
        for reservation in daily_reservations:
            parking_spot = reservation.parking_spot
            sensor = parking_spot.sensor
            if sensor.is_occupied:
                problem_parking_spots.append(parking_spot)
            reservation.status = "expired"
            reservation.save()

    def check_availability_monthly(self, problem_parking_spots):
        now = timezone.now()
        monthly_reservations = ParkingReservation.objects.filter(
            status="active",
            end_time__lte=now,
            tariff="monthly"
        )
        for reservation in monthly_reservations:
            parking_spot = reservation.parking_spot
            sensor = parking_spot.sensor
            if sensor.is_occupied:
                problem_parking_spots.append(parking_spot)
            reservation.status = "expired"
            reservation.save()

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



