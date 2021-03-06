from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart





def add_cart(request, product_id):
    product = Product.objects.get(id= product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            value = request.POST[item]
            try:
                variation = Variation.objects.get(product = product, variation_category__iexact = item, variation_value__iexact =value)
                product_variation.append(variation)
            except:
                pass

    try:

        cart = Cart.objects.get(cart_id= _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id= _cart_id(request))
    cart.save()


    is_cart_item_exist = CartItem.objects.filter(product = product, cart = cart).exists()
    if is_cart_item_exist:
        cart_item = CartItem.objects.filter(product = product, cart = cart)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        print(ex_var_list)

        if product_variation in ex_var_list:
            # increase quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product = product, id =item_id )
            item.quantity += 1
            item.save()

        else:
            # create a new item
            item = CartItem.objects.create(product = product, quantity = 1, cart= cart)
            if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            #cart_item.quantity += 1
            item.save()
    else:
            cart_item = CartItem.objects.create(product= product, quantity=1, cart= cart,)
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
    #return HttpResponse(cart_item.product)
    return redirect('cart')






def remove_cart(request, product_id, item_id):
    product = get_object_or_404(Product, id= product_id)
    cart = Cart.objects.get(cart_id= _cart_id(request))
    try:
        cart_item = CartItem.objects.get(product= product, cart= cart, id = item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, item_id):
    product = get_object_or_404(Product, id= product_id)
    cart = Cart.objects.get(cart_id = _cart_id(request))
    cart_item = CartItem.objects.get(product = product, cart = cart, id = item_id)
    cart_item.delete()
    return redirect('cart')






def cart(request, total_= 0, quantity= 0, cart_item= None):
    try:
        cart= Cart.objects.get(cart_id= _cart_id(request))
        cart_items= CartItem.objects.filter(cart= cart, is_active= True)
        for item in cart_items:

            total_+= item.quantity*item.product.price
        tax= (total_*2)/100
        grand_total= tax + total_
            #quantity+= item.quantity
    except ObjectDoesNotExist:
        pass


    context= {
            'total_': total_,
            'cart_items': cart_items,
            'tax': tax,
            'grand_total': grand_total

    }
    return render(request, 'store/cart.html', context)
