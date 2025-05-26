from django.urls import path
from . import views

urlpatterns = [
    path('', views.JuegoView.as_view(), name='juego')
]