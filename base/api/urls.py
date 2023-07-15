from django.urls import path
from . import views

urlpatterns =[
    path('', views.getRoute, name='route'),
    path('rooms/', views.getRooms, name='rooms'),
    path('room/<str:pk>/', views.getRoom, name='room'),
]