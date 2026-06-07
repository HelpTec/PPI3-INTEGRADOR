import requests
import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'twitch_token.json')


def _get_twitch_access_token():
    if os.path.exists(TOKEN_FILE_PATH):
        try:
            with open(TOKEN_FILE_PATH, 'r') as f:
                token_data = json.load(f)
            expiration_time = datetime.fromisoformat(token_data['expires_at'])
            if expiration_time > datetime.now() + timedelta(minutes=5):
                logger.debug("Using cached Twitch token, expires at %s", expiration_time)
                return token_data['access_token']
        except (json.JSONDecodeError, KeyError, ValueError):
            logger.debug("Cached token file invalid or expired, requesting new one.")

    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        logger.debug("Requesting new Twitch token...")
        response = requests.post(token_url, params=params)
        response.raise_for_status()
        token_response = response.json()
        logger.debug("Twitch token response status: %s", response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("Error getting Twitch token: %s", e)
        return None

    access_token = token_response.get("access_token")
    expires_in = token_response.get("expires_in")

    if access_token and expires_in:
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        try:
            with open(TOKEN_FILE_PATH, 'w') as f:
                json.dump({"access_token": access_token, "expires_at": expires_at.isoformat()}, f)
            logger.debug("New Twitch token cached. Expires in %s seconds.", expires_in)
        except OSError as e:
            logger.warning("Could not cache Twitch token: %s", e)
        return access_token

    logger.debug("Failed to obtain Twitch access token.")
    return None


def _igdb_post(headers, endpoint, query, timeout=8):
    try:
        resp = requests.post(
            f'https://api.igdb.com/v4/{endpoint}',
            headers=headers, data=query, timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("IGDB %s error: %s", endpoint, e)
        return []


def _img(image_id, size='t_cover_big'):
    return f"https://images.igdb.com/igdb/image/upload/{size}/{image_id}.jpg"


_AGE_RATING_LABELS = {1:'3+',2:'7+',3:'12+',4:'16+',5:'18+',
                      6:'RP',7:'EC',8:'E',9:'E10+',10:'T',11:'M',12:'AO'}
_AGE_RATING_ORG    = {1:'PEGI',2:'PEGI',3:'PEGI',4:'PEGI',5:'PEGI',
                      6:'ESRB',7:'ESRB',8:'ESRB',9:'ESRB',10:'ESRB',11:'ESRB',12:'ESRB'}


def _search_by_name(headers, fields, game_name):
    """
    Search strategy (in order):
    1. Exact name match, main release only (version_parent = null)
    2. Exact name match, any release
    3. Fuzzy search (IGDB's `search`)
    4. If name has '/', retry steps 1-3 with the first part only
    """
    def _exact(name):
        safe = name.replace('"', '').replace("'", "\\'")
        r = _igdb_post(headers, 'games',
                       f'fields {fields}; where name = "{safe}" & version_parent = null; limit 1;')
        if not r:
            r = _igdb_post(headers, 'games',
                           f'fields {fields}; where name = "{safe}"; limit 1;')
        return r

    def _fuzzy(name):
        safe = name.replace('"', '')
        return _igdb_post(headers, 'games', f'search "{safe}"; fields {fields}; limit 1;')

    results = _exact(game_name) or _fuzzy(game_name)

    if not results and '/' in game_name:
        first_part = game_name.split('/')[0].strip()
        results = _exact(first_part) or _fuzzy(first_part)

    return results


def get_full_game_detail(igdb_id=None, game_name=None):
    """
    Fetches full game detail from IGDB.
    Returns a rich dict with ratings, screenshots, videos, characters,
    similar games, alternative names, franchises, age ratings, engine.
    Prefer igdb_id; falls back to game_name search.
    """
    access_token = _get_twitch_access_token()
    if not access_token:
        return None

    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
    }

    fields = (
        "name, summary, storyline, first_release_date, "
        "genres.name, platforms.name, game_modes.name, "
        "involved_companies.company.name, involved_companies.developer, involved_companies.publisher, "
        "cover.image_id, "
        "screenshots.image_id, "
        "videos.video_id, videos.name, "
        "similar_games.name, similar_games.cover.image_id, "
        "alternative_names.name, alternative_names.comment, "
        "franchises.name, "
        "game_engines.name, "
        "age_ratings.rating, age_ratings.category, "
        "rating, total_rating_count, "
        "aggregated_rating, aggregated_rating_count"
    )

    if igdb_id:
        query = f'fields {fields}; where id = {igdb_id}; limit 1;'
        results = _igdb_post(headers, 'games', query)
    elif game_name:
        results = _search_by_name(headers, fields, game_name)
    else:
        return None

    if not results:
        return None
    d = results[0]
    resolved_igdb_id = d.get('id')

    developer = next(
        (c['company']['name'] for c in d.get('involved_companies', [])
         if isinstance(c, dict) and c.get('developer') and isinstance(c.get('company'), dict)),
        None
    )
    publisher = next(
        (c['company']['name'] for c in d.get('involved_companies', [])
         if isinstance(c, dict) and c.get('publisher') and isinstance(c.get('company'), dict)),
        None
    )

    cover_id = d.get('cover', {}).get('image_id') if isinstance(d.get('cover'), dict) else None
    screenshots = [
        _img(s['image_id'], 't_screenshot_big')
        for s in d.get('screenshots', [])
        if isinstance(s, dict) and s.get('image_id')
    ]

    year = None
    frd = d.get('first_release_date')
    if frd:
        from datetime import datetime as _dt
        year = _dt.utcfromtimestamp(frd).year

    videos = [
        {'video_id': v['video_id'], 'name': v.get('name', 'Trailer')}
        for v in d.get('videos', [])
        if isinstance(v, dict) and v.get('video_id')
    ][:3]

    similar = []
    for sg in d.get('similar_games', [])[:6]:
        if not isinstance(sg, dict):
            continue
        cover = sg.get('cover')
        cover_url = _img(cover['image_id'], 't_cover_small') if isinstance(cover, dict) and cover.get('image_id') else None
        similar.append({'name': sg.get('name', ''), 'cover_url': cover_url})

    alt_names = [
        {'name': an['name'], 'comment': an.get('comment', '')}
        for an in d.get('alternative_names', [])
        if isinstance(an, dict) and an.get('name')
    ][:8]

    franchises = [f['name'] for f in d.get('franchises', []) if isinstance(f, dict) and f.get('name')]
    engines = [e['name'] for e in d.get('game_engines', []) if isinstance(e, dict) and e.get('name')]

    age_ratings = []
    for ar in d.get('age_ratings', []):
        if not isinstance(ar, dict):
            continue
        rat = ar.get('rating')
        cat = ar.get('category')
        if cat and rat:
            age_ratings.append({
                'org':   _AGE_RATING_ORG.get(rat, 'IARC'),
                'label': _AGE_RATING_LABELS.get(rat, str(rat)),
            })

    characters = []
    if resolved_igdb_id:
        char_query = (
            f'fields name, mug_shot.image_id, species, gender, games; '
            f'where games = ({resolved_igdb_id}); limit 8;'
        )
        for ch in _igdb_post(headers, 'characters', char_query):
            if not isinstance(ch, dict):
                continue
            mug = ch.get('mug_shot')
            mug_url = _img(mug['image_id'], 't_thumb') if isinstance(mug, dict) and mug.get('image_id') else None
            characters.append({'name': ch.get('name', ''), 'mug_url': mug_url})

    return {
        'igdb_id':             resolved_igdb_id,
        'name':                d.get('name'),
        'summary':             d.get('summary') or d.get('storyline') or '',
        'year':                year,
        'genre':               d['genres'][0]['name'] if d.get('genres') and isinstance(d['genres'][0], dict) else None,
        'genres':              [g['name'] for g in d.get('genres', []) if isinstance(g, dict)],
        'platforms':           [p['name'] for p in d.get('platforms', []) if isinstance(p, dict)],
        'game_modes':          [m['name'] for m in d.get('game_modes', []) if isinstance(m, dict)],
        'developer':           developer,
        'publisher':           publisher,
        'cover_url':           _img(cover_id) if cover_id else None,
        'screenshots':         screenshots,
        'videos':              videos,
        'similar_games':       similar,
        'alt_names':           alt_names,
        'franchises':          franchises,
        'engines':             engines,
        'age_ratings':         age_ratings,
        'characters':          characters,
        'rating':              round(d['rating']) if d.get('rating') else None,
        'rating_count':        d.get('total_rating_count'),
        'critic_rating':       round(d['aggregated_rating']) if d.get('aggregated_rating') else None,
        'critic_rating_count': d.get('aggregated_rating_count'),
    }


def get_game_data_by_name(game_name):
    """
    Fetches game data from IGDB by game name.
    Returns a dict with image URL and metadata, or None if not found.
    """
    access_token = _get_twitch_access_token()
    if not access_token:
        logger.debug("get_game_data_by_name: No Twitch access token available.")
        return None

    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    query_body = (
        f'fields name, genres.name, platforms.name, release_dates.y, cover.url,'
        f'involved_companies.company.name, aggregated_rating, aggregated_rating_count,'
        f'total_rating, total_rating_count;'
        f'where name = "{game_name}";'
        f'limit 1;'
    )
    logger.debug("IGDB query for '%s'", game_name)

    try:
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers, data=query_body,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            logger.debug("No game found for '%s' in IGDB.", game_name)
            return None

        game_data = results[0]
        if not (game_data and game_data.get('name')):
            logger.debug("No suitable game data found for '%s'.", game_name)
            return None

        cover_url = None
        if game_data.get('cover') and game_data['cover'].get('url'):
            cover_url = game_data['cover']['url'].replace('thumb', 'cover_big')

        game_year = None
        for rd in game_data.get('release_dates', []):
            if isinstance(rd, dict) and rd.get('y'):
                game_year = rd['y']
                break

        genres = game_data.get('genres', [])
        platforms = game_data.get('platforms', [])
        companies = game_data.get('involved_companies', [])

        return {
            'API_ID':       str(game_data.get('id')),
            'Name':         game_data.get('name'),
            'Image_URL':    cover_url,
            'Year':         game_year,
            'Genre':        genres[0].get('name') if genres and isinstance(genres[0], dict) else None,
            'Platform':     platforms[0].get('name') if platforms and isinstance(platforms[0], dict) else None,
            'Publisher':    companies[0].get('company', {}).get('name') if companies and isinstance(companies[0], dict) else None,
            'Critic_Score': game_data.get('aggregated_rating'),
            'Critic_Count': game_data.get('aggregated_rating_count'),
            'User_Score':   game_data.get('total_rating'),
            'User_Count':   game_data.get('total_rating_count'),
        }

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error from IGDB for '%s': %s - %s", game_name, e.response.status_code, e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Request error fetching IGDB data for '%s': %s", game_name, e)
        return None
    except Exception as e:
        logger.error("Unexpected error in get_game_data_by_name for '%s': %s", game_name, e)
        return None
