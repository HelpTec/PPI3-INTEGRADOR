from django.shortcuts import render
from django.views.generic import TemplateView

class JuegoView(TemplateView):
    name = "home"
    template_name = "home.html"

class LoginView(TemplateView):
    name = "login"
    template_name = "login.html"

class GeneroView(TemplateView):
    name = "genero"
    template_name = "genero.html"