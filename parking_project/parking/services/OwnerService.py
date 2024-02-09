import logging

from django.db import transaction

from ..models import Owner, Address, ParkingSpot, ParkingSensor, Barrier, ParkingReservation, OwnerPayment
from ..services import QRCodeService

class OwnerService:

    @transaction.atomic
    def add_parking_spot(self, user, name, hourly_rate, daily_rate, monthly_rate, address, latitude, longitude):
        try:
            # Проверяем, является ли пользователь владельцем
            owner = Owner.objects.filter(user=user).first()

            # Если пользователь не является владельцем, создаем нового владельца
            if not owner:
                owner = Owner(user=user, bank_details="")  # Можете добавить банковские реквизиты по желанию
                owner.save()
                # Устанавливаем флаг is_owner пользователя в True
                user.is_owner = True
                user.save()

            # Проверяем, существует ли адрес в базе данных
            existing_address = Address.objects.filter(
                street=address['street'],
                city=address['city'],
                zip_code=address['zip_code'],
                country=address['country']
            ).first()

            # Если адрес существует, используем его, иначе создаем новый
            if existing_address:
                spot_address = existing_address
            else:
                spot_address = Address(
                    street=address['street'],
                    city=address['city'],
                    zip_code=address['zip_code'],
                    country=address['country'],
                )
                spot_address.save()

            # Создаем новое парковочное место с координатами
            spot = ParkingSpot(
                owner=owner,
                name=name,
                hourly_rate=hourly_rate,
                daily_rate=daily_rate,
                monthly_rate=monthly_rate,
                address=spot_address,
                latitude=latitude,
                longitude=longitude,
            )
            spot.save()

            # Создаем связанный сенсор
            sensor = ParkingSensor(name=f"Sensor for {name}", parking_spot=spot)
            sensor.save()

            # Создаем связанный запорный механизм
            barrier = Barrier(name=f"Barrier for {name}", sensor=sensor, parking_spot=spot)
            barrier.save()

            # Генерируем QR-код и сохраняем его в базе данных
            qr_code = QRCodeService.generate_qr_code(name, spot.id)

            # Логирование события
            logging.info(f"Добавлено новое парковочное место: {spot}")

            return "Парковочное место успешно добавлено."
        except Exception as e:
            # Логирование ошибки
            logging.error(f"Ошибка при добавлении парковочного места: {str(e)}")
            return f"Произошла ошибка при добавлении парковочного места: {str(e)}"

    def view_parking_spot_history(self, parking_spot, start_date, end_date):
        try:
            # Получаем все бронирования и платежи за выбранный период для конкретной парковки
            reservations = ParkingReservation.objects.filter(
                parking_spot=parking_spot,
                start_time__gte=start_date,
                end_time__lte=end_date
            )
            owner_payments = OwnerPayment.objects.filter(
                payment__reservation__in=reservations
            )

            # Создаем список для хранения истории
            history_entries = []

            # Добавляем бронирования в историю
            for reservation in reservations:
                history_entry = {
                    'type': 'Reservation',
                    'action_date': reservation.start_time,
                    'details': f"Reservation by {reservation.user.username} from {reservation.start_time} to {reservation.end_time}"
                }
                history_entries.append(history_entry)

            # Добавляем платежи в историю
            for owner_payment in owner_payments:
                history_entry = {
                    'type': 'OwnerPayment',
                    'action_date': owner_payment.timestamp,
                    'details': f"Owner Payment #{owner_payment.id} by {owner_payment.user.username} - Amount: {owner_payment.amount}"
                }
                history_entries.append(history_entry)

            # Сортируем историю по дате
            history_entries.sort(key=lambda x: x['action_date'])

            return history_entries
        except Exception as e:
            return f"Произошла ошибка при получении истории: {str(e)}"

    def update_hourly_rate(self, parking_spot, hourly_rate):
        try:
            # Обновляем часовую ставку для данной парковки
            parking_spot.hourly_rate = hourly_rate
            parking_spot.save()

            return "Часовая ставка для парковки успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении часовой ставки: {str(e)}"

    def update_daily_rate(self, parking_spot, daily_rate):
        try:
            # Обновляем дневную ставку для данной парковки
            parking_spot.daily_rate = daily_rate
            parking_spot.save()

            return "Дневная ставка для парковки успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении дневной ставки: {str(e)}"

    def update_monthly_rate(self, parking_spot, monthly_rate):
        try:
            # Обновляем месячную ставку для данной парковки
            parking_spot.monthly_rate = monthly_rate
            parking_spot.save()

            return "Месячная ставка для парковки успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении месячной ставки: {str(e)}"

    def set_hourly_availability(self, parking_spot, is_available):
        try:
            # Обновляем доступность парковки для бронирования по часам
            parking_spot.is_available_hourly = is_available
            parking_spot.save()

            return "Доступность парковки для бронирования по часам успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении доступности по часам: {str(e)}"

    def set_daily_availability(self, parking_spot, is_available):
        try:
            # Обновляем доступность парковки для дневного бронирования
            parking_spot.is_available_daily = is_available
            parking_spot.save()

            return "Доступность парковки для дневного бронирования успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении доступности для дневного бронирования: {str(e)}"

    def set_monthly_availability(self, parking_spot, is_available):
        try:
            # Обновляем доступность парковки для месячного бронирования
            parking_spot.is_available_monthly = is_available
            parking_spot.save()

            return "Доступность парковки для месячного бронирования успешно обновлена."
        except Exception as e:
            return f"Произошла ошибка при обновлении доступности для месячного бронирования: {str(e)}"