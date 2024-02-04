from ..models import Owner, Address

class OwnerService:
    # ...

    def view_address_history(self, owner):
        try:
            # Получаем все адреса, добавленные данным владельцем
            addresses = Address.objects.filter(owner=owner)

            # Создаем список для хранения истории адресов
            address_history = []

            # Перебираем адреса и формируем их историю
            for address in addresses:
                history_entry = {
                    'address': address.address,
                    'added_at': address.added_at,
                }
                address_history.append(history_entry)

            return address_history
        except Exception as e:
            return f"Произошла ошибка при получении истории адресов: {str(e)}"

