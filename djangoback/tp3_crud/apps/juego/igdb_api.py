# apps/juego/igdb_api.py
import requests
import os
import json
from datetime import datetime, timedelta

# Configuration from environment variables
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# IMPORTANT: You need to make sure these are actually loading.
# Add prints here to confirm they are not None.
print(f"DEBUG: TWITCH_CLIENT_ID loaded: {TWITCH_CLIENT_ID is not None}")
print(f"DEBUG: TWITCH_CLIENT_SECRET loaded: {TWITCH_CLIENT_SECRET is not None}")


TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'twitch_token.json') # Store token in app directory

def _get_twitch_access_token():
    """
    Obtains and manages the Twitch access token, caching it locally.
    """
    # ... (existing code for token caching) ...
    if os.path.exists(TOKEN_FILE_PATH):
        try:
            with open(TOKEN_FILE_PATH, 'r') as f:
                token_data = json.load(f)
            expiration_time = datetime.fromisoformat(token_data['expires_at'])
            # Refresh if token expires in less than 5 minutes
            if expiration_time > datetime.now() + timedelta(minutes=5):
                print(f"DEBUG: Using cached Twitch token, expires at {expiration_time}")
                return token_data['access_token']
        except (json.JSONDecodeError, KeyError, ValueError):
            print("DEBUG: Cached token file invalid or expired, requesting new one.")
            pass # Invalid token file, proceed to request new one

    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        print("DEBUG: Requesting new Twitch token...")
        response = requests.post(token_url, params=params)
        response.raise_for_status()
        token_response = response.json()
        print(f"DEBUG: Twitch token response status: {response.status_code}")
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
        print(f"DEBUG: New Twitch token obtained and cached. Expires in {expires_in} seconds.")
        return access_token
    else:
        print("DEBUG: Failed to obtain Twitch access token (missing access_token or expires_in).")
        return None

def get_game_data_by_name(game_name):
    """
    Fetches game data from IGDB by game name, including image URL.
    Returns a dictionary of game data or None if not found/error.
    """
    access_token = _get_twitch_access_token()
    if not access_token:
        print("DEBUG: get_game_data_by_name: No Twitch access token available.")
        return None

    headers = {
        'Client-ID': TWITCH_CLIENT_ID, # Uses the same Client ID
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    search_url = 'https://api.igdb.com/v4/games'
    query_body = f"""
    search "{game_name}";
    fields name, genres.name, platforms.name, release_dates.y, cover.url,
           involved_companies.company.name, aggregated_rating, aggregated_rating_count,
           total_rating, total_rating_count;
    limit 1; # We only want the best match
    """
    print(f"DEBUG: IGDB API Query Body:\n{query_body}")

    try:
        print(f"DEBUG: Making IGDB API request for game: '{game_name}'...")
        response = requests.post(search_url, headers=headers, data=query_body)
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)
        results = response.json()
        print(f"DEBUG: IGDB API Response (first 200 chars):\n{str(results)[:200]}...")

        if results:
            game_data = results[0] # Take the first result
            print(f"DEBUG: Found game data for '{game_data.get('name')}' (ID: {game_data.get('id')}).")
            # Process the cover URL to get a larger size
            cover_url = None
            if game_data.get('cover') and game_data['cover'].get('url'):
                cover_url = game_data['cover']['url'].replace('thumb', 'cover_big')
                print(f"DEBUG: Raw IGDB cover URL: {game_data['cover']['url']}")
                print(f"DEBUG: Processed cover URL: {cover_url}")
            else:
                print("DEBUG: No 'cover' or 'cover.url' found in IGDB response for this game.")

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
            print(f"DEBUG: No game found for '{game_name}' in IGDB results.")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP Error from IGDB API for '{game_name}': {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: General Request Error fetching game data from IGDB for '{game_name}': {e}")
        return None
    except Exception as e: # Catch any other unexpected errors during processing
        print(f"ERROR: Unexpected error in get_game_data_by_name for '{game_name}': {e}")
        return None