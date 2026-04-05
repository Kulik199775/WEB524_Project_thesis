from .cart import Cart


def cart(request):
    """Контекстный процессор для добавления корзины в каждый шаблон"""
    return {'cart': Cart(request)}