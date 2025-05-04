from django.urls import path
from . import views

urlpatterns = [
    path('', views.simple_map, name='simple_map'),
    path('hello/', views.hello_api, name='hello_api'),  # exemple d'endpoint
]