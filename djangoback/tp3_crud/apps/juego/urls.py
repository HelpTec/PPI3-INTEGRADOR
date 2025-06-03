from django.urls import path
from . import views

urlpatterns = [
    path('juego', views.JuegoView.as_view(), name='juego'),
    path('', views.LoginAuth, name='login'),
    path('register', views.register_view, name='register'),
    path('genero', views.GeneroView.as_view(), name='genero')
]