from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from apps.juego.models import Juego
from .igdb_api import get_game_data_by_name
import json 

class JuegoView(TemplateView):
    name = "home"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["juegos"] = Juego.objects.all()
        return context

# apps/juego/views.py

# In apps/juego/views.py

# ... (other code) ...


def detalle_juego(request, juego_id):
    print(f"--- DEBUG: Entering detalle_juego view for ID: {juego_id} ---")

    juego = get_object_or_404(Juego, id=juego_id)

    print(f"\n--- DEBUG: Detalle Juego View for '{juego.Name}' (ID: {juego_id}) ---")
    print(f"DEBUG: Current Image_URL in DB: {juego.Image_URL}")

    print(f"DEBUG: Always attempting to fetch/update data for {juego.Name} from IGDB...")
    # Temporarily hardcode a simple game name for API test

    api_data = get_game_data_by_name(juego.Name) # Use the temporary name here!

    print(f"DEBUG: API Data received: {api_data}")

    if api_data:
        # ... (your existing update logic) ...
        # Make sure you are updating fields from api_data, not hardcoding them
        juego.Image_URL = api_data.get('Image_URL')
        juego.API_ID = api_data.get('API_ID')
        juego.Year = api_data.get('Year') # Add these back if you removed them
        juego.Genre = api_data.get('Genre')
        juego.Platform = api_data.get('Platform')
        juego.Publisher = api_data.get('Publisher')
        juego.Critic_Score = api_data.get('Critic_Score')
        juego.Critic_Count = api_data.get('Critic_Count')
        juego.User_Score = api_data.get('User_Score')
        juego.User_Count = api_data.get('User_Count')
        # ... (any other fields) ...

        try:
            juego.save()
            print(f"DEBUG: Successfully updated {juego.Name} with new data from IGDB.")
            print(f"DEBUG: New Image_URL after save: {juego.Image_URL}")
        except Exception as e:
            print(f"ERROR: Error saving updated game data for {juego.Name}: {e}")
    else:
        print(f"DEBUG: Could not find any data from IGDB for {juego.Name} (API call returned None/empty).")
    # --- End: Logic to fetch and update ALL relevant fields from API ---

    sales_data = {
        'NA_Sales': float(juego.NA_Sales) if juego.NA_Sales is not None else 0.0,
        'EU_Sales': float(juego.EU_Sales) if juego.EU_Sales is not None else 0.0,
        'JP_Sales': float(juego.JP_Sales) if juego.JP_Sales is not None else 0.0,
        'Other_Sales': float(juego.Other_Sales) if juego.Other_Sales is not None else 0.0,
        'Global_Sales': float(juego.Global_Sales) if juego.Global_Sales is not None else 0.0,
    }
    sales_data_json = json.dumps(sales_data)    
    context = {
        'juego': juego,
        'sales_data_json': sales_data_json, # Pass the JSON string to the template
    }
    return render(request, 'juego.html', context)

class GeneroView(TemplateView):
    name = "genero"
    template_name = "genero.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["juegos"] = Juego.objects.all()
        return context


class PlataformaView(TemplateView):
    name = "plataforma"
    template_name = "plataforma.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["juegos"] = Juego.objects.all()
        return context


class DecadaView(TemplateView):
    name = "decada"
    template_name = "decada.html"

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
