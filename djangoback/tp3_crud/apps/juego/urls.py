from django.urls import path, include
from . import views

urlpatterns = [
    path("juego", views.JuegoView.as_view(), name="juego"),
    path("", views.LoginAuth, name="login"),
    path("register", views.register_view, name="register"),
    path("genero", views.GeneroView.as_view(), name="genero"),
    path("plataforma", views.PlataformaView.as_view(), name="plataforma"),
    path("decada", views.DecadaView.as_view(), name="plataforma"),
    path('juego/<int:juego_id>/', views.detalle_juego, name='detalle_juego'),
]
