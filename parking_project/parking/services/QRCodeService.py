from io import BytesIO

import qrcode

from ..models import  ParkingSpot, QRCode


class QRCodeService:
    @staticmethod
    def generate_qr_code(parking_spot_name, parking_spot_id):
        """
        Генерирует QR-код для парковочного места по его имени и ID.
        QR-код содержит информацию о имени и ID парковочного места.
        """
        try:
            qr_data = f"Парковочное место: {parking_spot_name}, ID: {parking_spot_id}"

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

            # Сохранение изображения QR-кода в базе данных
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Сохранение QR-кода в базе данных
            qr_code = QRCode(name=f"Parking Spot {parking_spot_id}", image=img_bytes.read())
            qr_code.save()

            return qr_code  # Возвращение объекта QRCode, который можно предоставить клиентам
        except Exception as e:
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
