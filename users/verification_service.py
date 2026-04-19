from django.core.cache import cache
from django.utils import timezone
from .services import generate_verification_code, send_verification_code, is_code_valid
from .models import User


class VerificationService:
    """Сервис для управления кодами подтверждения через кэш"""

    CACHE_PREFIX = 'verification_code_'
    CACHE_EXPIRY = 600  # 10 минут в секундах

    @classmethod
    def _get_cache_key(cls, email):
        """Получить ключ для кэша"""
        return f'{cls.CACHE_PREFIX}{email}'

    @classmethod
    def send_code(cls, email):
        """Отправить код подтверждения на email"""
        # Генерируем код
        code = generate_verification_code()

        # Сохраняем код в кэш
        cache_key = cls._get_cache_key(email)
        cache.set(cache_key, {
            'code': code,
            'created_at': timezone.now().isoformat(),
            'attempts': 0
        }, cls.CACHE_EXPIRY)

        # Получаем пользователя для персонализации
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass

        # Отправляем код на email
        send_verification_code(email, code, user)

        return True

    @classmethod
    def verify_code(cls, email, code):
        """Проверить код подтверждения"""
        cache_key = cls._get_cache_key(email)
        data = cache.get(cache_key)

        if not data:
            return False, 'Код не найден или истек срок действия'

        # Проверяем количество попыток
        if data.get('attempts', 0) >= 3:
            cache.delete(cache_key)
            return False, 'Превышено количество попыток. Запросите новый код'

        # Проверяем код
        stored_code = data.get('code')
        created_at = timezone.datetime.fromisoformat(data.get('created_at'))

        if not is_code_valid(created_at):
            cache.delete(cache_key)
            return False, 'Код истек. Запросите новый код'

        if stored_code != code:
            # Увеличиваем счетчик попыток
            data['attempts'] = data.get('attempts', 0) + 1
            cache.set(cache_key, data, cls.CACHE_EXPIRY)
            remaining = 3 - data['attempts']
            return False, f'Неверный код. Осталось попыток: {remaining}'

        # Код верный - удаляем из кэша
        cache.delete(cache_key)
        return True, 'Код подтвержден'

    @classmethod
    def clear_code(cls, email):
        """Удалить код из кэша"""
        cache_key = cls._get_cache_key(email)
        cache.delete(cache_key)