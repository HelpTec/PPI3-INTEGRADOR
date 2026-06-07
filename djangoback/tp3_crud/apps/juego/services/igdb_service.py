import logging
from django.db.models import Q
from ..models import Juego
from ..igdb_api import get_full_game_detail
from ..deepl_translate import translate_to_spanish
from .game_service import PLAYABLE_PLATFORMS

logger = logging.getLogger(__name__)

_DB_SIMILAR_LIMIT = 6


def get_enriched_game(game_id: int) -> dict | None:
    """
    Fetch game by PK, enrich with IGDB data, and translate the summary to Spanish.
    Caches translated summary and cover URL back to the model.
    If IGDB returns no similar games, falls back to DB-based similarity.
    Returns the enriched data dict, or None if the game or IGDB data is not found.
    """
    try:
        juego = Juego.objects.get(pk=game_id)
    except Juego.DoesNotExist:
        return None

    igdb_id = juego.API_ID
    data = get_full_game_detail(
        igdb_id=int(igdb_id) if igdb_id and igdb_id.isdigit() else None,
        game_name=juego.Name,
    )
    if data is None:
        return None

    _apply_summary_cache(juego, data)
    _persist_derived_fields(juego, data)

    if not data.get('similar_games'):
        data['similar_games'] = _get_db_similar_games(juego)

    return data


def _get_db_similar_games(juego, limit=_DB_SIMILAR_LIMIT) -> list:
    """
    Find similar games in the local DB.
    Strategy: same genre + same platform first; pad with same genre if needed.
    Returns a list of dicts compatible with the frontend similar-games tile format.
    """
    base_qs = Juego.objects.exclude(pk=juego.pk).order_by('Rank', 'id')

    results = []
    if juego.Genre and juego.Platform:
        results = list(
            base_qs.filter(Genre=juego.Genre, Platform=juego.Platform)[:limit]
        )

    if len(results) < limit and juego.Genre:
        existing_ids = [g.id for g in results]
        extra = base_qs.filter(Genre=juego.Genre).exclude(pk__in=existing_ids)[: limit - len(results)]
        results.extend(extra)

    return [_db_game_to_similar(g) for g in results]


def _db_game_to_similar(g) -> dict:
    """Shape a Juego instance into the similar-games dict the frontend expects."""
    return {
        'id':           g.id,
        'name':         g.Name or '',
        'cover_url':    g.Image_URL or None,
        'image_url':    g.Image_URL or '',
        'platform':     g.Platform or '',
        'year':         g.Year,
        'genre':        g.Genre or '',
        'publisher':    g.Publisher or '',
        'global_sales': float(g.Global_Sales) if g.Global_Sales else 0,
        'playable':     (g.Platform or '') in PLAYABLE_PLATFORMS,
    }


def _apply_summary_cache(juego, data):
    """Use cached Spanish summary if available; otherwise translate and cache it."""
    if juego.Summary_ES:
        data['summary'] = juego.Summary_ES
    elif data.get('summary'):
        translated = translate_to_spanish(data['summary'])
        data['summary'] = translated
        juego.Summary_ES = translated


def _persist_derived_fields(juego, data):
    """Save cover URL, API ID, and translated summary back to the model when changed."""
    update_fields = []
    if data.get('cover_url') and data['cover_url'] != juego.Image_URL:
        juego.Image_URL = data['cover_url']
        update_fields.append('Image_URL')
    if data.get('igdb_id') and not juego.API_ID:
        juego.API_ID = str(data['igdb_id'])
        update_fields.append('API_ID')
    if juego.Summary_ES and 'Summary_ES' not in update_fields:
        update_fields.append('Summary_ES')
    if update_fields:
        try:
            juego.save(update_fields=update_fields)
        except Exception:
            pass
