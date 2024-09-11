from django.urls import path
from . import views  #from accounts import views  ya accounts ki jgh . use kre qki same directory
from accounts.views import cart
from products.views import add_to_cart

urlpatterns = [
    path('sign/', views.sign, name='sign'),
    path('login/', views.handlelogin, name='handlelogin'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('activate/<uid64>/<token>' , views.ActivateAccountView.as_view(),name='activate'),
    path('cart/', cart, name="cart"),
    path('add-to-cart/<uid>/',add_to_cart,name="add_to_cart"),
]