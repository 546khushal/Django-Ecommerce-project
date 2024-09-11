from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from design import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    
   
    ]