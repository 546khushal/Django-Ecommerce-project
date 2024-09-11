from django.urls import path
from . import views

urlpatterns = [
   path('product/<slug:slug>/', views.get_product, name='get_product'),
    #path('pro/', views.products, name='products'),
  
]


