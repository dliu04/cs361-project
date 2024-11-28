import os
import spotipy
import json

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def refresh_token(token_info):
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id='e3ee009e9bc04a5dbb8f9a62a6d6f923', client_secret='7be4c70da1944a92818d3ef2291c9afc', redirect_uri='http://127.0.0.1:5000/redirect')
    token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    with open('token_info.json', 'w') as f:
        json.dump(token_info, f)
    return token_info