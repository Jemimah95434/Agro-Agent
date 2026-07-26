from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend),
    path('chat/', views.chat),
    path('yield_trend/', views.yield_trend),
]