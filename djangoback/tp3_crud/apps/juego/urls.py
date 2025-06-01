from django.urls import path
from . import views

urlpatterns = [
    path('juego', views.JuegoView.as_view(), name='juego'),
    path('', views.LoginView.as_view(), name='login'),
    path('genero', views.GeneroView.as_view(), name='genero')
]