import json
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Juego
from ..igdb_api import get_game_data_by_name

logger = logging.getLogger(__name__)


@login_required
def detalle_juego(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id)

    api_data = get_game_data_by_name(juego.Name)
    if api_data:
        juego.Image_URL = api_data.get('Image_URL')
        juego.API_ID = api_data.get('API_ID')
        juego.Year = api_data.get('Year')
        juego.Genre = api_data.get('Genre')
        juego.Platform = api_data.get('Platform')
        juego.Publisher = api_data.get('Publisher')
        juego.Critic_Score = api_data.get('Critic_Score')
        juego.Critic_Count = api_data.get('Critic_Count')
        juego.User_Score = api_data.get('User_Score')
        juego.User_Count = api_data.get('User_Count')
        try:
            juego.save()
        except Exception as e:
            logger.error("Error guardando %s: %s", juego.Name, e)
    else:
        logger.warning("No se encontró data IGDB para '%s'", juego.Name)

    sales_data = {
        'NA_Sales':     float(juego.NA_Sales)     if juego.NA_Sales     is not None else 0.0,
        'EU_Sales':     float(juego.EU_Sales)     if juego.EU_Sales     is not None else 0.0,
        'JP_Sales':     float(juego.JP_Sales)     if juego.JP_Sales     is not None else 0.0,
        'Other_Sales':  float(juego.Other_Sales)  if juego.Other_Sales  is not None else 0.0,
        'Global_Sales': float(juego.Global_Sales) if juego.Global_Sales is not None else 0.0,
    }
    return render(request, 'juego.html', {
        'juego': juego,
        'sales_data_json': json.dumps(sales_data),
    })
