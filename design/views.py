from django.shortcuts import render,redirect
from django.contrib import messages
from products.models import Product,Category
from math import ceil

# Create your views here.
def index(request):
    allProds = []
    categories = Category.objects.all()
    for cat in categories:
        products = Product.objects.filter(category=cat)
        n = len(products)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append((products, range(1, nSlides), nSlides))

    context = {'allProds': allProds}
    return render(request,'base/index.html',context)
    
def contact(request):
    return render(request,'base/contact.html')

def about(request):
    return render(request,'base/about.html')
def sign(request):
    return render(request,'base/sign.html')