import qrcode
from io import BytesIO
from ..models import ParkingSpot  # Импортируйте модель ParkingSpot


class QRCodeService:

    @staticmethod
    def generate_qr_code(parking_spot_id):
        """
        Генерирует QR-код для парковочного места по его ID.
        QR-код содержит информацию о ID и имени парковочного места.
        """
        try:
            # Поиск парковочного места по ID
            parking_spot = ParkingSpot.objects.get(id=parking_spot_id)
            qr_data = f"Парковочное место: {parking_spot.name}, ID: {parking_spot.id}"

            # Создание QR-кода
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Генерация изображения QR-кода
            img = qr.make_image(fill='black', back_color='white')

            # Сохранение изображения в память
            img_bytes = BytesIO()
            img.save(img_bytes)
            img_bytes.seek(0)

            # Возвращаем байты изображения
            return img_bytes.getvalue()

        except ParkingSpot.DoesNotExist:
            return None

    @staticmethod
    def find_parking_spot_by_qr_data(qr_data):
        """
        Находит парковочное место по данным из QR-кода.
        QR-код должен содержать ID парковочного места.
        """
        # Извлекаем ID из данных QR-кода
        try:
            # Предполагаем, что qr_data имеет формат "Парковочное место: <имя>, ID: <id>"
            parking_spot_id = qr_data.split(", ID: ")[1]
            parking_spot = ParkingSpot.objects.get(id=parking_spot_id)
            return parking_spot
        except (IndexError, ParkingSpot.DoesNotExist):
            return None
