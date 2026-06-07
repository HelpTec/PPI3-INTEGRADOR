import json
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ..services.game_service import search_games, get_shelves
from ..services.igdb_service import get_enriched_game
from ..services.chat_service import get_chat_reply

logger = logging.getLogger(__name__)


@login_required
def gamebase_view(request):
    return render(request, 'gamebase.html')


@login_required
def api_juegos(request):
    q         = request.GET.get('q', '').strip()
    platform  = request.GET.get('platform', '').strip()
    year_from = request.GET.get('year_from', '').strip()
    year_to   = request.GET.get('year_to', '').strip()
    page      = int(request.GET.get('page', 1))

    if q or platform or year_from or year_to:
        data = search_games(
            q=q,
            platform=platform,
            year_from=int(year_from) if year_from else None,
            year_to=int(year_to) if year_to else None,
            page=page,
        )
    else:
        data = get_shelves()
    return JsonResponse(data)


@login_required
def api_igdb_ficha(request):
    game_id = request.GET.get('game_id')
    if not game_id:
        return JsonResponse({'error': 'game_id requerido'}, status=400)
    data = get_enriched_game(int(game_id))
    if data is None:
        return JsonResponse({'error': 'not found'}, status=404)
    return JsonResponse(data)


@login_required
@csrf_exempt
def api_chat_bot(request):
    if request.method != 'POST':
        return JsonResponse({'reply': 'Método no permitido.'}, status=405)
    try:
        body = json.loads(request.body)
        reply = get_chat_reply(body.get('message', ''))
        return JsonResponse({'reply': reply})
    except ValueError as e:
        msg = str(e)
        if msg == 'empty_message':
            return JsonResponse({'reply': 'Mensaje vacío.'}, status=400)
        if msg == 'missing_api_key':
            return JsonResponse({'reply': 'La clave de API de Gemini no está configurada.'}, status=500)
        return JsonResponse({'reply': msg}, status=500)
    except Exception as e:
        logger.error('Error en api_chat_bot: %s', e)
        return JsonResponse({'reply': f'Hubo un error de IA: {str(e)}'}, status=500)
