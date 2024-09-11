from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModels
from products.models import Product,ColorVariant,SizeVariant
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
    is_paid= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItems(BaseModels):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    color_variant = models.ForeignKey(ColorVariant,on_delete=models.SET_NULL,null=True,blank=True)
    size_variant = models.ForeignKey(SizeVariant,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)