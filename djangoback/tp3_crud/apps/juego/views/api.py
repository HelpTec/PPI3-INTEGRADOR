import json
import os
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
import google.generativeai as genai
from ..models import Juego
from ..igdb_api import get_full_game_detail
from .juegos import PLAYABLE_PLATFORMS, SHELF_PLATFORMS, SHELF_LABELS

logger = logging.getLogger(__name__)


@login_required
def gamebase_view(request):
    return render(request, 'gamebase.html')


@login_required
@csrf_exempt
def api_chat_bot(request):
    if request.method != 'POST':
        return JsonResponse({'reply': 'Método no permitido.'}, status=405)
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        if not user_message:
            return JsonResponse({'reply': 'Mensaje vacío.'}, status=400)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "TU_CLAVE_DE_GEMINI_AQUI":
            return JsonResponse({'reply': 'La clave de API de Gemini no está configurada.'}, status=500)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            "Eres un asistente virtual de una página web sobre videojuegos llamada GameBase. "
            "Responde de forma amistosa, útil y concisa al siguiente mensaje del usuario:\n\n"
            f"Usuario: {user_message}"
        )
        response = model.generate_content(prompt)
        return JsonResponse({'reply': response.text})
    except Exception as e:
        logger.error("Error en api_chat_bot: %s", e)
        return JsonResponse({'reply': f'Hubo un error de IA: {str(e)}'}, status=500)


@login_required
def api_igdb_ficha(request):
    game_id = request.GET.get('game_id')
    if not game_id:
        return JsonResponse({'error': 'game_id requerido'}, status=400)
    try:
        juego = Juego.objects.get(pk=game_id)
    except Juego.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)
    igdb_id = juego.API_ID
    data = get_full_game_detail(
        igdb_id=int(igdb_id) if igdb_id and igdb_id.isdigit() else None,
        game_name=juego.Name,
    )
    if data is None:
        return JsonResponse({'error': 'no igdb data'}, status=404)
    if data.get('cover_url') and data['cover_url'] != juego.Image_URL:
        try:
            juego.Image_URL = data['cover_url']
            juego.save(update_fields=['Image_URL'])
        except Exception:
            pass
    return JsonResponse(data)


@login_required
def api_juegos(request):
    q = request.GET.get('q', '').strip()
    platform = request.GET.get('platform', '').strip()
    page = int(request.GET.get('page', 1))
    PER_PAGE = 40

    def game_dict(g):
        return {
            'id':           g.id,
            'name':         g.Name or '',
            'platform':     g.Platform or '',
            'year':         g.Year,
            'genre':        g.Genre or '',
            'publisher':    g.Publisher or '',
            'image_url':    g.Image_URL or '',
            'global_sales': float(g.Global_Sales) if g.Global_Sales else 0,
            'playable':     (g.Platform or '') in PLAYABLE_PLATFORMS,
        }

    if q or platform:
        qs = Juego.objects.all()
        if q:
            qs = qs.filter(
                Q(Name__icontains=q) | Q(Platform__icontains=q) | Q(Genre__icontains=q)
            )
        if platform and platform != 'all':
            qs = qs.filter(Platform__iexact=platform)
        qs = qs.order_by('Rank', 'id')
        paginator = Paginator(qs, PER_PAGE)
        page_obj = paginator.get_page(page)
        return JsonResponse({
            'mode':  'search',
            'games': [game_dict(g) for g in page_obj],
            'total': paginator.count,
            'pages': paginator.num_pages,
            'page':  page_obj.number,
        })

    all_platforms = list(
        Juego.objects.values_list('Platform', flat=True)
        .distinct().order_by('Platform')
    )
    shelves = []
    for plat in SHELF_PLATFORMS:
        if plat not in all_platforms:
            continue
        games = list(
            Juego.objects.filter(Platform__iexact=plat).order_by('Rank', 'id')[:20]
        )
        if games:
            shelves.append({
                'platform': plat,
                'label':    SHELF_LABELS.get(plat, plat),
                'games':    [game_dict(g) for g in games],
            })

    return JsonResponse({
        'mode':      'shelves',
        'shelves':   shelves,
        'platforms': all_platforms,
    })
