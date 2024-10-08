from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModels
from products.models import Coupon, Product,ColorVariant,SizeVariant
# Create your models here.
class Profile(BaseModels):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified =models.BooleanField(default=False)
    email_token = models.CharField(max_length=100 , null=True ,blank= True)
    profile_image = models.ImageField(upload_to="profile")


    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid=False, cart__user=self.user).count()

class Cart(BaseModels):
    user =models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True,blank=True)
    is_paid= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    razor_pay_order_id =models.CharField(max_length=100,null=True, blank =True)
    razor_pay_payment_id =models.CharField(max_length=100,null=True, blank =True)
    razor_pay_payment_signature =models.CharField(max_length=100,null=True, blank =True)
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []

        # Calculate the total price based on product and variant prices
        for cart_item in cart_items:
            price.append(cart_item.product.price)  # Add base product price
            if cart_item.color_variant:
                color_variant_price = cart_item.color_variant.price
                price.append(color_variant_price)  # Add color variant price if available
            if cart_item.size_variant:
                size_variant_price = cart_item.size_variant.price
                price.append(size_variant_price)  # Add size variant price if available
        
        total_price = sum(price)  # Total price before discount

        # Apply coupon discount if available
        if self.coupon:
            total_price -= self.coupon.discount_price  # Subtract the coupon discount
        
        # Ensure the total doesn't go below 0
        return max(total_price, 0)


    def __str__(self):
        return f"{self.user.username}'s cart"

    @staticmethod
    def get_cart_count(user):
        return Cart.objects.filter(user=user).count()


class CartItems(BaseModels):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    color_variant = models.ForeignKey(ColorVariant,on_delete=models.SET_NULL,null=True,blank=True)
    size_variant = models.ForeignKey(SizeVariant,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def get_product_price(self):
        price =[self.product.price]

        if self.color_variant:
            color_variant_price =self.color_variant.price
            price.append(color_variant_price)
        if self.size_variant:
            size_variant_price =self.size_variant.price
            price.append(size_variant_price)
        return sum(price)