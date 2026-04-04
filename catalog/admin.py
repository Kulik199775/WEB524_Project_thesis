from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category, SkinType, Ingredient, Product, Favorite

from decimal import Decimal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями товаров"""
    list_display = ('name', 'parent', 'order', 'is_active', 'products_count', 'image_preview')
    list_display_links = ('name',)
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at', 'image_preview_large')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Визуальное оформление', {
            'fields': ('image', 'image_preview_large', 'order'),
            'classes': ('collapse',)
        }),
        ('Статус и даты', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def products_count(self, obj):
        """Подсчет количества товаров в категории"""
        count = obj.products.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    products_count.short_description = 'Товаров'

    def image_preview(self, obj):
        """Представление изображения в списке"""
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return format_html('<span style="color: gray;">Нет фото</span>')
    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        """Крупное представление для детальной информации"""
        if obj.image:
            return format_html('<img src="{}" style="width: 200px; height: auto;" />', obj.image.url)
        return 'Нет изображения'
    image_preview_large.short_description = 'Изображение'

    actions = ['activate_categories', 'deactivate_categories']

    @admin.action(description='Активировать выбранные категории')
    def activate_categories(self, request, queryset):
        """Активация выбранных категорий"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} категорий.')

    @admin.action(description='Деактивировать выбранные категории')
    def deactivate_categories(self, request, queryset):
        """Деактивация выбранных категорий"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} категорий.')

@admin.register(SkinType)
class SkinTypeAdmin(admin.ModelAdmin):
    """Управление типами кожи"""
    list_display = ('name', 'products_count', 'created_at', 'icon_display')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    readonly_fields = ('created_at', 'products_list')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Оформление', {
            'fields': ('icon', 'icon_display_preview'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('products_list', 'created_at'),
            'classes': ('collapse',)
        })
    )

    def products_count(self, obj):
        """Количество товаров для данного типа кожи"""
        count = obj.products.count()
        return format_html('<span style="color: #2bde3f; font-weight: bold;">{} товаров</span>', count)
    products_count.short_description = 'Товаров'

    def products_list(self, obj):
        """Список товаров для детальной страницы"""
        products = obj.products.all()[:10]
        if products:
            return format_html('<br>'.join([f'• {p.name}' for p in products]))
        return 'Нет товаров'
    products_list.short_description = 'Товары с этим типом кожи'

    def icon_display(self, obj):
        """Отображение иконки в списке"""
        if obj.icon:
            return format_html('<i class="{}" style="font-size: 20px;"></i>', obj.icon)
        return '-'
    icon_display.short_description = 'Иконка'

    def icon_display_preview(self, obj):
        """Представление иконки в детальной странице"""
        if obj.icon:
            return format_html('<i class="{}" style="font-size: 40px;"></i><br>Класс: {}', obj.icon, obj.icon)
        return 'Иконка не задана'
    icon_display_preview.short_description = 'Превью иконки'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Управление ингредиентами"""
    list_display = ('name', 'is_natural', 'is_organic', 'is_allergen', 'products_count', 'status_badge')
    list_display_links = ('name',)
    list_filter = ('is_natural', 'is_organic', 'is_allergen')
    search_fields = ('name', 'scientific_name', 'description')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at', 'products_list', 'image_preview_large')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'scientific_name', 'description', 'benefits')
        }),
        ('Характеристики', {
            'fields': ('is_natural', 'is_organic', 'is_allergen'),
            'classes': ('wide',)
        }),
        ('Визуальное оформление', {
            'fields': ('image', 'image_preview_large'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('products_list', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def products_count(self, obj):
        """Количества товаров с этим ингредиентом"""
        count = obj.products.count()
        color = '#2bde3f' if count > 10 else '#ffc107' if count > 0 else '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, count)
    products_count.short_description = 'Товаров'

    def products_list(self, obj):
        """Список товаров содержащих ингредиент"""
        products = obj.products.all()[:15]
        if products:
            return format_html('<br>'.join([f'• {p.name}' for p in products]))
        return 'Нет товаров с этим ингредиентом'
    products_list.short_description = 'Товары в составе'

    def status_badge(self, obj):
        """Бейдж статуса ингредиента"""
        badges = []
        if obj.is_natural:
            badges.append('<span style="color: green;">🌿 Натуральный</span>')
        if obj.is_organic:
            badges.append('<span style="color: #28a745;">✅ Органический</span>')
        if obj.is_allergen:
            badges.append('<span style="color: red;">⚠️ Аллерген</span>')
        return format_html('<br>'.join(badges) if badges else '-')
    status_badge.short_description = 'Свойства'

    def image_preview_large(self, obj):
        """Представление изображения"""
        if obj.image:
            return format_html('<img src="{}" style="width: 150px; height: auto;" />', obj.image.url)
        return 'Нет изображения'
    image_preview_large.short_description = 'Изображение'

    actions = ['mark_as_natural', 'mark_as_allergen']

    @admin.action(description='Отметить как натуральные')
    def mark_as_natural(self, request, queryset):
        queryset.update(is_natural=True)
        self.message_user(request, f'Отмечено {queryset.count()} ингредиентов как натуральные.')

    @admin.action(description='Отметить как аллергены')
    def mark_as_allergen(self, request, queryset):
        queryset.update(is_allergen=True)
        self.message_user(request, f'Отмечено {queryset.count()} ингредиентов как аллергены.')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Для управления товарами"""
    list_display = ('name', 'price', 'stock', 'is_available', 'category', 'tags_display', 'image_preview')
    list_display_links = ('name',)
    list_filter = ('category', 'skin_types', 'ingredients', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'sku')
    list_editable = ('price', 'stock')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at', 'image_preview_large', 'stock_status')

    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'sku', 'category')
        }),
        ('Цены и остатки', {
            'fields': ('price', 'stock', 'stock_status', 'volume'),
            'classes': ('wide',)
        }),
        ('Характеристики', {
            'fields': ('skin_types', 'ingredients'),
            'classes': ('wide',)
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview_large'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('is_active', 'is_new', 'is_bestseller', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    filter_horizontal = ('skin_types', 'ingredients')
    inlines = []

    def is_available(self, obj):
        """Отображение доступности товара"""
        if obj.is_available:
            return format_html('<span style="color: green; font-weight: bold;">✓ В наличии</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Нет в наличии</span>')

    is_available.short_description = 'Доступность'
    is_available.admin_order_field = 'stock'

    def stock_status(self, obj):
        """Статус остатка с цветовой индикацией"""
        if obj.stock > 50:
            return format_html('<span style="color: green;">🟢 Много ({} шт.)</span>', obj.stock)
        elif obj.stock > 10:
            return format_html('<span style="color: orange;">🟡 Средне ({} шт.)</span>', obj.stock)
        elif obj.stock > 0:
            return format_html('<span style="color: red;">🔴 Мало ({} шт.)</span>', obj.stock)
        return format_html('<span style="color: gray;">⚫ Нет в наличии</span>')

    stock_status.short_description = 'Состояние склада'

    def tags_display(self, obj):
        """Отображение тегов/меток товара"""
        tags = []
        if obj.is_new:
            tags.append(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px;">🆕 Новинка</span>')
        if obj.is_bestseller:
            tags.append(
                '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px;">⭐ Хит</span>')
        if not obj.is_available:
            tags.append(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px;">📦 Нет в наличии</span>')
        return format_html(' '.join(tags)) if tags else '-'

    tags_display.short_description = 'Метки'

    def image_preview(self, obj):
        """Превью изображения в списке"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url)
        return format_html('<span style="color: gray;">📷 Нет фото</span>')

    image_preview.short_description = 'Фото'

    def image_preview_large(self, obj):
        """Крупное превью для детальной страницы"""
        if obj.image:
            return format_html('<img src="{}" style="width: 200px; height: auto; border-radius: 10px;" />',
                               obj.image.url)
        return 'Нет изображения'

    image_preview_large.short_description = 'Превью'

    actions = ['mark_available', 'mark_unavailable', 'increase_price', 'decrease_price']

    @admin.action(description='Отметить как в наличии (если остаток > 0)')
    def mark_available(self, request, queryset):
        """Отметить товары как доступные (ничего не меняет, просто уведомление)"""
        count = queryset.filter(stock__gt=0).count()
        self.message_user(request, f'{count} товаров уже в наличии или будут добавлены.')

    @admin.action(description='Отметить как распродано')
    def mark_unavailable(self, request, queryset):
        """Установить остаток в 0 для выбранных товаров"""
        updated = queryset.update(stock=0)
        self.message_user(request, f'{updated} товаров отмечены как распроданные.')

    @admin.action(description='Увеличить цену на 10%')
    def increase_price(self, request, queryset):
        """Увеличение цены на 10%"""
        for product in queryset:
            product.price = product.price * Decimal('1.1')
            product.save()
        self.message_user(request, f'Цена увеличена для {queryset.count()} товаров.')

    @admin.action(description='Уменьшить цену на 10%')
    def decrease_price(self, request, queryset):
        """Уменьшение цены на 10%"""
        for product in queryset:
            product.price = product.price * Decimal('0.9')
            product.save()
        self.message_user(request, f'Цена уменьшена для {queryset.count()} товаров.')

    def save_model(self, request, obj, form, change):
        """Переопределение сохранения для логирования"""
        if change:
            self.message_user(request, f'Товар "{obj.name}" успешно обновлен.', level='SUCCESS')
        else:
            self.message_user(request, f'Товар "{obj.name}" успешно создан.', level='SUCCESS')
        super().save_model(request, obj, form, change)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Для управления избранными товарами пользователей"""
    list_display = ('user_info', 'product_info', 'created_at', 'days_ago')
    list_display_links = ('user_info',)
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'product__name')
    readonly_fields = ('created_at',)
    list_per_page = 30
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('user', 'user_full_info')
        }),
        ('Информация о товаре', {
            'fields': ('product', 'product_full_info')
        }),
        ('Дата', {
            'fields': ('created_at', 'days_ago')
        })
    )

    def user_info(self, obj):
        """Отображение информации о пользователе"""
        return format_html(
            '<strong>{}</strong><br><span style="color: gray;">{}</span>',
            obj.user.email,
            obj.user.get_full_name() or 'Не указано имя'
        )
    user_info.short_description = 'Пользователь'

    def product_info(self, obj):
        """Отображение информации о товаре"""
        return format_html(
            '<strong>{}</strong><br><span style="color: gray;">₽ {}</span>',
            obj.product.name,
            obj.product.price
        )

    product_info.short_description = 'Товар'

    def user_full_info(self, obj):
        """Полная информация о пользователе (только для чтения)"""
        return format_html(
            '<b>Email:</b> {}<br><b>Имя:</b> {}<br><b>Телефон:</b> {}',
            obj.user.email,
            obj.user.get_full_name() or '-',
            obj.user.phone or '-'
        )

    user_full_info.short_description = 'Детали пользователя'

    def product_full_info(self, obj):
        """Полная информация о товаре (только для чтения)"""
        return format_html(
            '<b>Название:</b> {}<br><b>Цена:</b> ₽ {}<br><b>Категория:</b> {}<br><b>В наличии:</b> {}',
            obj.product.name,
            obj.product.price,
            obj.product.category or '-',
            'Да' if obj.product.is_available else 'Нет'
        )

    product_full_info.short_description = 'Детали товара'

    def days_ago(self, obj):
        """Сколько дней назад добавлено в избранное"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        days = delta.days
        if days == 0:
            return 'Сегодня'
        elif days == 1:
            return 'Вчера'
        return f'{days} дней назад'

    days_ago.short_description = 'Давность'

    actions = ['export_selected_favorites']

    @admin.action(description='Экспортировать выбранные записи')
    def export_selected_favorites(self, request, queryset):
        """Экспорт выбранных записей в CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="favorites_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Email пользователя', 'Товар', 'Дата добавления'])

        for favorite in queryset:
            writer.writerow([favorite.user.email, favorite.product.name, favorite.created_at])

        self.message_user(request, f'Экспортировано {queryset.count()} записей.')
        return response