from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from apps.juego.models import Juego
from django.core.paginator import Paginator
from .igdb_api import get_game_data_by_name
import json
import os
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class JuegoView(TemplateView):
    name = "home"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #creo la lista para el paginador
        juegos_qs = Juego.objects.all()
        #cuantos juegos por lista se generan y el argumento del paginador
        paginator = Paginator(juegos_qs, 5)
        #esto extrae en que pagina estamos para el indice, tambien guarda los 5 juegos
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        #la funcion que agrega las imagenes de la api
        for juego in page_obj.object_list:
            api_data = get_game_data_by_name(juego.Name)
            if api_data:
                juego.Image_URL = api_data.get("Image_URL")
                try:
                    juego.save()
                except Exception as e:
                    print(f"Error guardando {juego.Name}: {e}")
        #con esto el context tiene los datos que queremos
        context["page_obj"] = page_obj
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
        #aca recibimos el genero
        genero = self.request.GET.get("genero")
        #creo una lista vacia
        juegos_qs = Juego.objects.none()
        #llenamos la lista con juegos del genero
        if genero:
            juegos_qs = Juego.objects.filter(Genre__iexact=genero)
        paginator = Paginator(juegos_qs, 5)
        #repito el proceso de la pagina general y listo
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        for juego in page_obj.object_list:
            api_data = get_game_data_by_name(juego.Name)
            if api_data:
                juego.Image_URL = api_data.get("Image_URL")
                try:
                    juego.save()
                except Exception as e:
                    print(f"Error guardando {juego.Name}: {e}")
        context["page_obj"] = page_obj
        context["genero_actual"] = genero
        return context


class PlataformaView(TemplateView):
    name = "plataforma"
    template_name = "plataforma.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #aca recibimos la plataforma
        plataforma = self.request.GET.get("plataforma")
        #creo una lista vacia
        juegos_qs = Juego.objects.none()
        #llenamos la lista con juegos de la plataforma
        if plataforma:
            juegos_qs = Juego.objects.filter(Platform__iexact=plataforma)
        paginator = Paginator(juegos_qs, 5)
        #repito el proceso de la pagina general y listo
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        for juego in page_obj.object_list:
            api_data = get_game_data_by_name(juego.Name)
            if api_data:
                juego.Image_URL = api_data.get("Image_URL")
                try:
                    juego.save()
                except Exception as e:
                    print(f"Error guardando {juego.Name}: {e}")
        context["page_obj"] = page_obj
        context["plataforma_actual"] = plataforma
        return context


class DecadaView(TemplateView):
    name = "decada"
    template_name = "decada.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #aca recibimos la decada
        decada_str = self.request.GET.get("decada")
        #lista vacia y variable vacia
        juegos_qs = Juego.objects.all()
        decada_actual = None
        #llenamos la lista con juegos de la plataforma
        if decada_str:
            try:
                decada = int(decada_str)
                print(decada)
                juegos_qs = juegos_qs.filter(Year__gte=decada, Year__lt=decada + 10)
                decada_actual = decada
            except ValueError:
                pass
        else:
            juegos_qs = ()
            
        paginator = Paginator(juegos_qs, 5)
        #repito el proceso de la pagina general y listo
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        for juego in page_obj.object_list:
            api_data = get_game_data_by_name(juego.Name)
            if api_data:
                juego.Image_URL = api_data.get("Image_URL")
                try:
                    juego.save()
                except Exception as e:
                    print(f"Error guardando {juego.Name}: {e}")
        context["page_obj"] = page_obj
        context["decada_actual"] = decada_actual
        return context


def LoginAuth(request):
    """
    Vista de login que usa el backend LDAP3 personalizado
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Validar que se proporcionaron ambos campos
        if not username or not password:
            messages.error(request, "Por favor ingrese usuario y contraseña")
            return render(request, "login.html")

        # Intentar autenticar con LDAP
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido {user.first_name or user.username}!")
            return redirect("home")
        else:
            messages.error(
                request,
                "Usuario o contraseña incorrectos. Verifique sus credenciales."
            )

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


@csrf_exempt
def api_chat_bot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'reply': 'Mensaje vacío.'}, status=400)
                
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key or api_key == "TU_CLAVE_DE_GEMINI_AQUI":
                return JsonResponse({'reply': 'La clave de API de Gemini no está configurada.'}, status=500)
            
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                "Eres un asistente virtual de una página web sobre videojuegos llamada GameBase. "
                "Responde de forma amistosa, útil y concisa al siguiente mensaje del usuario:\n\n"
                f"Usuario: {user_message}"
            )
            
            response = model.generate_content(prompt)
            
            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'reply': f'Hubo un error de IA: {str(e)}'}, status=500)
    
    return JsonResponse({'reply': 'Método no permitido.'}, status=405)
