from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product, SizeVariant
from accounts.models import Cart, CartItems,Profile
from django.http import HttpResponseRedirect
from django.urls import reverse

def get_product(request, slug):
    try:
        # Retrieve the product based on the slug
        product = get_object_or_404(Product, slug=slug)

        # Initialize the context with the product
        context = {'product': product}

        # Get the cart item count if the user has a profile
        if request.user.is_authenticated:
            try:
                cart_count = request.user.profile.get_cart_count()
                context['cart_count'] = cart_count
            except Profile.DoesNotExist:
                # Handle the case where the user doesn't have a profile
                context['cart_count'] = 0
        else:
            # If the user is not authenticated, cart count is 0
            context['cart_count'] = 0

        # Check if a size parameter is provided and update context accordingly
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size 
            context['updated_price'] = price

        # Render the template with the context
        return render(request, 'products/pro.html', context=context)
    
    except Exception as e:
        # Print the exception for debugging purposes
        print(e)
        return render(request, 'products/pro.html', context={'error': 'An error occurred.'})


def add_to_cart(request, uid):
    if not request.user.is_authenticated:
        # Redirect to the login page if the user is not authenticated
        return redirect(f"{reverse('handlelogin')}?next={request.get_full_path()}")
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


def pro(request):
    return render(request, 'products/pro.html')
