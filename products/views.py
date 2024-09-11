from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product, SizeVariant
from accounts.models import Cart, CartItems
from django.http import HttpResponseRedirect

def get_product(request, slug):
    print('******')
    print(request.user)
    
    # Check if the user has a profile
    if hasattr(request.user, 'profile'):
        print(request.user.profile.get_cart_count)
    else:
        print("User does not have a profile")
    
    print('******')
    
    product = get_object_or_404(Product, slug=slug)
    context = {'product': product}
    
    if request.GET.get('size'):
        size = request.GET.get('size')
        price = product.get_product_price_by_size(size)
        context['selected_size'] = size 
        context['updated_price'] = price
    
    return render(request, 'products/pro.html', context=context)


def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    
    # Fetch the product using the UID
    product = Product.objects.get(uid=uid)
    user = request.user
    
    # Get or create a cart for the user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    
    # Create a CartItem instance
    cart_item = CartItems.objects.create(cart=cart, product=product)
    
    # If a variant is selected, associate it with the CartItem
    if variant:
        size_variant = SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant = size_variant
        cart_item.save()
    
    # Redirect back to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
