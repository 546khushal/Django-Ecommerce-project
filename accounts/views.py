from multiprocessing.connection import Client
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .models import Profile  # Import the Profile model

from products.models import Coupon, Product, SizeVariant
from accounts.models import Cart, CartItems,Profile
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import razorpay

# User Registration
def sign(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        c_password = request.POST.get('pass2')

        if password != c_password:
            messages.warning(request, "Passwords do not match.")
            return redirect('/accounts/sign/')

        try:
            if User.objects.filter(username=email).exists():
                messages.info(request, "Email already exists.")
                return redirect('/accounts/sign/')
                
        except Exception as identifier:
            pass

        # Create the new user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        # Create a Profile for the new user
        profile = Profile.objects.create(user=user)
        profile.save()

        # Send activation email
        email_subject = "Activate Your Account"
        message = render_to_string('accounts/activate.html', {
            'user': user,
            'domain': 'http://127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()

        messages.success(request, "Please activate your account via the email sent to you.")
        return redirect('/accounts/login/')

    return render(request, 'accounts/sign.html')

# Account Activation
class ActivateAccountView(View):
    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, "Account Activated Successfully")
            return redirect('/accounts/login/')
        
        return render(request, 'accounts/activatefail.html')

# User Login
def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get('email')
        userpassword = request.POST.get('pass1')
        user_obj = User.objects.filter(username=username).first()

        if not user_obj:
            messages.warning(request, "Email Not Found!")
            return redirect('/accounts/login')

        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Successfully")
            return redirect('/')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('/accounts/login')
        
    return render(request, 'accounts/login.html')

# User Logout
def handlelogout(request):
    logout(request)
    messages.info(request, "Logged out successfully! Please login again.")
    return redirect('/accounts/login')


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


def remove_cart(request, cart_item_uid):
    try:
        cart_item =CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
        
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Redirect for cart (this can be modified based on your cart implementation)
from django.conf import settings
def cart(request):
    if request.user.is_authenticated:
        try:
            # Get the user's unpaid cart
            user_cart = Cart.objects.get(is_paid=False, user=request.user)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))  # Razorpay client

            # Get cart items for the user
            cart_items = CartItems.objects.filter(cart=user_cart)

            if request.method == 'POST':
                print("POST request received")
                
                # Get the coupon code from the POST request
                coupon_code = request.POST.get('coupon')
                print(f"Coupon code entered: {coupon_code}")

                # Validate the coupon
                coupon_obj = Coupon.objects.filter(Coupon_code__icontains=coupon_code)

                if not coupon_obj.exists():
                    messages.warning(request, "Invalid Coupon.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                coupon = coupon_obj.first()

                # Check if a coupon is already applied to the cart
                if user_cart.coupon:
                    messages.info(request, "Coupon Already Applied.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                # Ensure the cart total meets the minimum coupon requirement
                if user_cart.get_cart_total() < coupon.minimum_amount:
                    messages.info(request, f'Cart amount should be greater than {coupon.minimum_amount}.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                # Check if the coupon is expired
                if coupon.is_expired:
                    messages.info(request, "Coupon expired.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                # Apply the coupon to the user's cart
                user_cart.coupon = coupon
                user_cart.save()
                messages.success(request, "Coupon Applied Successfully.")

            # After coupon validation or by default, create a Razorpay order
            try:
                amount_to_pay = user_cart.get_cart_total() * 100  # Amount in paise (INR)
                print(f"Creating Razorpay order for amount: {amount_to_pay}")

                # Create Razorpay order
                payment = client.order.create({
                    'amount': amount_to_pay, 
                    'currency': 'INR', 
                    'payment_capture': 1
                })

                print(f"Razorpay order created: {payment}")

                # Attach the Razorpay order ID to the cart object (assuming the field exists in your model)
                user_cart.razorpay_order_id = payment['id']  # Ensure you have this field in your Cart model
                user_cart.save()

            except Exception as e:
                print(f"Error during Razorpay payment creation: {str(e)}")
                messages.error(request, "Payment creation failed.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            context = {
                'cart_items': cart_items,
                'user_cart': user_cart,
                'payment': payment,  # Passing the Razorpay order details to the template
                'razorpay_key': settings.RAZORPAY_KEY,  # Razorpay public key for the frontend
            }

        except Cart.DoesNotExist:
            context = {
                'cart_items': [],
                'user_cart': None,
            }

        return render(request, 'accounts/cart.html', context)
    else:
        return redirect('handlelogin')

    

def remove_coupon(request, cart_id):
    if request.user.is_authenticated:
        # Change 'id' to 'uid' for UUID filtering
        user_cart = get_object_or_404(Cart, uid=cart_id, is_paid=False, user=request.user)
        user_cart.coupon = None  # Remove the coupon
        user_cart.save()
        messages.success(request, "Coupon removed successfully.")
    else:
        messages.warning(request, "You need to log in to remove a coupon.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def success(request):
    order_id = request.GET.get('order_id')
    
    try:
        cart = Cart.objects.get(razor_pay_order_id=order_id)
        cart.is_paid = True
        cart.save()
        return render(request, 'success.html', {'message': 'Payment was successful!'})
    except Cart.DoesNotExist:
        return HttpResponse('Order ID not found in the database.', status=404)