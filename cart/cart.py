from django.conf import settings
from catalog.models import Product


class Cart:
    """Для управления корзиной покупок"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """Добавление товара в корзину или увеличение его количества"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        new_quantity = self.cart[product_id]['quantity'] + quantity

        if new_quantity <= product.stock:
            self.cart[product_id]['quantity'] = new_quantity
            self.save()
            return True
        return False

    def remove(self, product_id):
        """Удаление товара из корзины"""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product_id, quantity):
        """Обновление количества товара в корзине"""
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                product = Product.objects.get(id=int(product_id))
                if quantity <= product.stock:
                    self.cart[product_id]['quantity'] = quantity
                    self.save()
                    return True
            else:
                self.remove(product_id)
                return True
        return False

    def save(self):
        """Сохраняет текущее состояние корзины в сессию"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        """Полностью очищает корзину"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['total_price'] = float(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())
