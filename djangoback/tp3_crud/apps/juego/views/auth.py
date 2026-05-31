from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def LoginAuth(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "Por favor ingrese usuario y contraseña")
            return render(request, "login.html")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Usuario o contraseña incorrectos. Verifique sus credenciales.")
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("home")
        messages.error(request, "Porfavor, corrija errores e intente nuevamente")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})
