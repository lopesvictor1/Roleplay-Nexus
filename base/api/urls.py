from django.urls import path
from . import views

urlpatterns =[
    path('', views.getRoute, name='route'),
    path('rooms/', views.getRooms, name='api-rooms'),
    path('room/<str:pk>/', views.getRoom, name='api-room'),
]