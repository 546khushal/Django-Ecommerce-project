from django.contrib import admin
from base.models import BaseModels
from products.models import Category,Product,ProductImages,ColorVariant,SizeVariant,Coupon
# Register your models here.
admin.site.register(Category)
admin.site.register(Coupon)


class ProductImagesAdmin(admin.StackedInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    list_display =['product_name','price']
    inlines =[ProductImagesAdmin]


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display =['color_name','price']
    model = ColorVariant

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display =['size_name','price']
    model = SizeVariant

admin.site.register(Product,ProductAdmin)

admin.site.register(ProductImages)
