from carts.models import Cart, CartItem
from carts.views import _cart_id

def counter(request):
    count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart= cart)
            for item in cart_items:
                count += item.quantity
        except Cart.DoesNotExist:
            count = 0
    return dict(count=count)
