from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from apps.juego.models import Juego

class JuegoView(TemplateView):
    name = "home"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["juegos"] = Juego.objects.all()
        return context

class GeneroView(TemplateView):
    name = "genero"
    template_name = "genero.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["juegos"] = Juego.objects.all()
        return context

def LoginAuth(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("juego")
        else:
            messages.error(request, "Usuario o Contraseña incorrectos")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario Creado con exito!")
            return redirect("login")
        else:
            messages.error(request, "Porfavor, corrija errores e intente nuevamente")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})