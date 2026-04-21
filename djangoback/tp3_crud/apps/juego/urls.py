from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.JuegoView.as_view(), name="home"),
    path("login", views.LoginAuth, name="login"),
    path("register", views.register_view, name="register"),
    path("genero", views.GeneroView.as_view(), name="genero"),
    path("plataforma", views.PlataformaView.as_view(), name="plataforma"),
    path("decada", views.DecadaView.as_view(), name="decada"),
    path('juego/<int:juego_id>/', views.detalle_juego, name='detalle_juego'),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("api/chat/", views.api_chat_bot, name="api_chat_bot"),
    path("emujs/", views.Emujs.as_view(), name="emujs"),
]
