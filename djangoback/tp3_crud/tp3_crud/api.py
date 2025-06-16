# apps/juego/igdb_api.py
import requests
import os
import json
from datetime import datetime, timedelta

# Configuration from environment variables
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'twitch_token.json') # Store token in app directory

def _get_twitch_access_token():
    """
    Obtains and manages the Twitch access token, caching it locally.
    """
    if os.path.exists(TOKEN_FILE_PATH):
        try:
            with open(TOKEN_FILE_PATH, 'r') as f:
                token_data = json.load(f)
            expiration_time = datetime.fromisoformat(token_data['expires_at'])
            # Refresh if token expires in less than 5 minutes
            if expiration_time > datetime.now() + timedelta(minutes=5):
                return token_data['access_token']
        except (json.JSONDecodeError, KeyError, ValueError):
            pass # Invalid token file, proceed to request new one

    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(token_url, params=params)
        response.raise_for_status()
        token_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting Twitch token: {e}")
        return None

    access_token = token_response.get("access_token")
    expires_in = token_response.get("expires_in")

    if access_token and expires_in:
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        cached_data = {
            "access_token": access_token,
            "expires_at": expires_at.isoformat()
        }
        with open(TOKEN_FILE_PATH, 'w') as f:
            json.dump(cached_data, f)
        return access_token
    else:
        return None

def get_game_data_by_name(game_name):
    """
    Fetches game data from IGDB by game name, including image URL.
    Returns a dictionary of game data or None if not found/error.
    """
    access_token = _get_twitch_access_token()
    if not access_token:
        print("Could not get Twitch access token for IGDB API.")
        return None

    headers = {
        'Client-ID': TWITCH_CLIENT_ID, # Uses the same Client ID
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    search_url = 'https://api.igdb.com/v4/games'
    # Use 'search' for exact name lookup, then 'where' to filter and get fields
    query_body = f"""
    search "{game_name}";
    fields name, genres.name, platforms.name, release_dates.y, cover.url,
           involved_companies.company.name, aggregated_rating, aggregated_rating_count,
           total_rating, total_rating_count;
    limit 1; # We only want the best match
    """

    try:
        response = requests.post(search_url, headers=headers, data=query_body)
        response.raise_for_status()
        results = response.json()

        if results:
            game_data = results[0] # Take the first result
            # Process the cover URL to get a larger size
            cover_url = None
            if game_data.get('cover') and game_data['cover'].get('url'):
                # IGDB provides a 'thumb' URL by default, replace it for a larger version
                cover_url = game_data['cover']['url'].replace('thumb', 'cover_big') # or '1080p' if you need very high res

            return {
                'API_ID': str(game_data.get('id')),
                'Name': game_data.get('name'),
                'Image_URL': cover_url,
                'Year': game_data['release_dates'][0]['y'] if game_data.get('release_dates') else None,
                'Genre': game_data['genres'][0]['name'] if game_data.get('genres') else None,
                'Platform': game_data['platforms'][0]['platform']['name'] if game_data.get('platforms') else None,
                'Publisher': game_data['involved_companies'][0]['company']['name'] if game_data.get('involved_companies') else None,
                'Critic_Score': game_data.get('aggregated_rating'),
                'Critic_Count': game_data.get('aggregated_rating_count'),
                'User_Score': game_data.get('total_rating'),
                'User_Count': game_data.get('total_rating_count'),
            }
        else:
            print(f"No game found for '{game_name}'.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game data from IGDB for '{game_name}': {e}")
        return None
    
    # From apps/juego/igdb_api.py

def get_game_data_by_name(game_name):
    access_token = _get_twitch_access_token()
    if not access_token:
        print("Could not get Twitch access token for IGDB API.")
        return None

    headers = {
        'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    search_url = 'https://api.igdb.com/v4/games'
    
    # *** THIS IS THE CRUCIAL PART FOR IMAGES ***
    query_body = f"""
    search "{game_name}";
    fields name, genres.name, platforms.name, release_dates.y, cover.url, screenshots.url,
           involved_companies.company.name, aggregated_rating, aggregated_rating_count,
           total_rating, total_rating_count;
    limit 1;
    """
    # *****************************************

    try:
        response = requests.post(search_url, headers=headers, data=query_body)
        response.raise_for_status()
        results = response.json()

        if results:
            game_data = results[0]

            # --- Processing the Image URLs ---
            cover_url = None
            if game_data.get('cover') and game_data['cover'].get('url'):
                # The 'url' from IGDB is often for a small thumbnail ('thumb').
                # You can replace the size identifier to get a larger version.
                # Common replacements: 'thumb' -> 'cover_big', '1080p', 'screenshot_big', etc.
                # Check IGDB's image size documentation for available options.
                cover_url = game_data['cover']['url'].replace('thumb', 'cover_big')
            
            screenshots_urls = []
            if game_data.get('screenshots'):
                for screenshot in game_data['screenshots']:
                    if screenshot.get('url'):
                        # Replace 'thumb' with a larger size for screenshots
                        screenshots_urls.append(screenshot['url'].replace('thumb', 'screenshot_big'))

            return {
                'API_ID': str(game_data.get('id')),
                'Name': game_data.get('name'),
                'Image_URL': cover_url, # This is your main game cover
                'Screenshots_URLs': screenshots_urls, # New field for screenshots if you want them
                'Year': game_data['release_dates'][0]['y'] if game_data.get('release_dates') else None,
                # ... other fields ...
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game data from IGDB for '{game_name}': {e}")
        return None