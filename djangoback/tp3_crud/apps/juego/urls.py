from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.gamebase_view, name="home"),
    path("api/juegos/", views.api_juegos, name="api_juegos"),
    path("api/igdb-ficha/", views.api_igdb_ficha, name="api_igdb_ficha"),
    path("api/chat/", views.api_chat_bot, name="api_chat_bot"),
    path("login", views.LoginAuth, name="login"),
    path("register", views.register_view, name="register"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
