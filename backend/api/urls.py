from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('crop/', views.crop_recommendation),
    path('fertilizer/', views.fertilizer_recommendation),
    path('recommend/', views.recommend),
    path('chat/', views.chat),
    path('yield_trend/', views.yield_trend),
]
