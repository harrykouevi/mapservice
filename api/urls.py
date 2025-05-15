from django.urls import path
from . import views

urlpatterns = [
    path('', views.simple_map, name='simple_map'),
    path('map-with-issues-around', views.map_with_road_issues_around, name='map_with_road_issues_around'),
    path('map-directions', views.map_direction, name='map_direction'),
    path('hello/', views.hello_api, name='hello_api'),  # exemple d'endpoint
]