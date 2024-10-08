from django.db import models
from base.models import BaseModels
from django.utils.text import slugify


# Create your models here.
class Category(BaseModels):
    category_name =models.CharField(max_length=100)
    category_image =models.ImageField(upload_to="category")
    slug =models.SlugField(unique=True , null= True, blank= True ) #jaise url :1800/3223/1 ya 2 aise dikh rha to hm watch,cloth aise dikhayenge

    def save(self,*args,**kwargs):
        self.slug= slugify(self.category_name)
        super(Category,self).save(*args,**kwargs)

    def __str__(self) -> str:
        return self.category_name


class ColorVariant(BaseModels):
    color_name =models.CharField(max_length=100)
    price =models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name

class SizeVariant(BaseModels):
    size_name= models.CharField(max_length=100)
    price =models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class Product(BaseModels):
    product_name =models.CharField(max_length=100)
    category =models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    slug =models.SlugField(unique=True , null= True, blank= True )
    price =models.IntegerField()
    product_description = models.TextField()
    color_variant =models.ManyToManyField(ColorVariant,blank=True)
    size_variant =models.ManyToManyField(SizeVariant ,blank=True)

    def save(self,*args,**kwargs):
        self.slug= slugify(self.product_name)
        super(Product,self).save(*args,**kwargs)

    def __str__(self) -> str:
        return self.product_name
    
    def get_product_price_by_size(self,size):
        return self.price + SizeVariant.objects.get(size_name = size).price



class ProductImages(BaseModels):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    images =models.ImageField(upload_to="products")

class Coupon(BaseModels):
    Coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price =models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)