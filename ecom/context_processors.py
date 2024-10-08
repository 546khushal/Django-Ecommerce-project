# ecom/context_processors.py

from accounts.models import Profile

def cart_count(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            cart_count = profile.get_cart_count()
        except Profile.DoesNotExist:
            cart_count = 0
    else:
        cart_count = 0
    return {'cart_count': cart_count}
