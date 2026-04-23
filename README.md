# Kasmia - Интернет-магазин натуральной косметики

Kasmia — это интернет-магазин натуральной косметики, разработанный на Django с использованием 
современных технологий кэширования, асинхронных запросов и адаптивного дизайна.

## Основные возможности

### Каталог товаров
- Фильтрация по цене, рейтингу, наличию и типу кожи
- Сортировка (по цене, новизне, названию)
- Пагинация (6 товаров на страницу)
- Поиск по названию товара
- Кэширование списков для неавторизованных пользователей

### Система пользователей
- Регистрация и аутентификация (email/пароль)
- Вход по одноразовому коду на email
- Личный кабинет с редактированием профиля
- Загрузка аватара
- Ролевая модель: пользователь, модератор, администратор

### Корзина и заказы
- Добавление/удаление товаров, изменение количества
- Хранение корзины в сессии
- Оформление заказа (адрес, телефон, способ оплаты)
- История заказов в личном кабинете
- Проверка остатков при оформлении

### Избранное
- Добавление/удаление через AJAX без перезагрузки
- Отдельная страница со списком избранных товаров
- Состояние сохраняется для авторизованных пользователей

### Система отзывов и рейтингов
- Оценка товара от 1 до 5 звезд
- Модерация отзывов (доступна модераторам)
- Проверка отзывов на запрещённые слова перед отправкой на модерацию (better-profanity)
- Отображение среднего рейтинга и распределения оценок
- Защита от спама и ссылок

### Производительность и оптимизация
- Redis кэширование (списки товаров, категории, детальные страницы)
- Debounce для оптимизации формы фильтрации
- AJAX-запросы для корзины и избранного
- CSRF-защита для всех POST-запросов

### UI/UX
- Адаптивный дизайн на Bootstrap 5
- Тёмная и светлая темы (сохраняется в localStorage)
- Кастомные toast-уведомления
- Анимация при скролле (AOS)
- Sticky-эффект для изображения товара
- Кнопка "Наверх" с плавной прокруткой

## Технологии

**Backend** | Python 3.13, Django 6.0 
**База данных** | MS SQL Server 
**Кэширование** | Redis, django-redis 
**Frontend** | Bootstrap 5, Bootstrap Icons, AOS 
**JavaScript** | Чистый JS (AJAX) 
**Почта** | SMTP (Яндекс) 
**Дополнительно** | python-dotenv, Pillow, better-profanity, flake8 

## Требования

- Python 3.13 или выше
- Redis сервер (для кэширования)
- MS SQL Server (или SQLite для разработки)
- Git

## Настройка виртуального окружения:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## Установка зависимостей:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Настройка переменных окружения:
```
Отредактируйте .env и заполните свои данные:

- База данных MS SQL Server
MS_SQL_USER='your_username'
MS_SQL_KEY='your_password'
MS_SQL_SERVER='YOUR_SERVER\SQLEXPRESS'
MS_SQL_DATABASE='WEB524_Project_thesis'
MS_SQL_PAD_DATABASE='master'
MS_SQL_DRIVER='ODBC Driver 18 for SQL Server'

-Email для уведомлений (Яндекс)
EMAIL_HOST_USER='your_email@yandex.ru'
YANDEX_PASSWORD_APP='your_app_password'

- Redis кэширование
CACHED_ENABLED=True
CACHE_LOCATION=redis://127.0.0.1:6379
```

### Установка и запуск Redis
- Windows (через WSL2):

```bash
wsl --install
wsl
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping  # Должно вернуть PONG
```

- Windows (через установщик MSI):
 1. Скачайте Redis с https://github.com/tporadowski/redis/releases
 2. Установите и запустите Redis

- Linux/macOS:

```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
```

- Проверка работы Redis:

```bash
redis-cli ping
# Должно вернуть: PONG
```

## Создание базы данных
```bash
python manage.py ccdb
```

## Создание и применение миграций
```bash
python manage.py makemigrations # создание миграций
python manage.py migrate # применение миграций
```

## Создание суперпользователя (администратора)
```bash
python manage.py ccsu
```

## Запуск Redis сервера
```bash
redis-server
```

## Запуск сервера
```bash
python manage.py runserver
```