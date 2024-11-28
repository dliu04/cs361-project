import json
import time
import requests
import threading
import webbrowser
from flask import Flask, redirect, url_for, session, request
from authorize import create_spotify_oauth
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

TOKEN_INFO = 'token_info'

def get_token_info():
    try:
        with open('token_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_token_info(token_info):
    with open('token_info.json', 'w') as f:
        json.dump(token_info, f)

def is_token_expired(token_info):
    now = int(time.time())
    return token_info['expires_at'] - now < 60

def refresh_access_token(token_info):
    spotify_oauth = create_spotify_oauth()
    token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    save_token_info(token_info)
    return token_info

def test_access_token(token_info):
    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.status_code == 200

def fetch_audio_feature(token_info, track_id):
    headers = {
        "Authorization": f"Bearer {token_info['access_token']}"
    }
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch audio feature. Status code: {response.status_code}")
        return None

def get_client_credentials_token():
    client_id = 'e3ee009e9bc04a5dbb8f9a62a6d6f923'
    client_secret = '7be4c70da1944a92818d3ef2291c9afc'
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'client_credentials'
        },
        headers={
            'Authorization': f'Basic {base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()}'
        }
    )
    return auth_response.json()

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    spotify_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = spotify_oauth.get_access_token(code)
    save_token_info(token_info)
    session[TOKEN_INFO] = token_info
    return "Login successful! You can close this window."

def start_flask_server():
    app.run(port=5000)

def main():
    token_info = get_token_info()

    if not token_info:
        print("No token info found. Starting Flask server for user login...")
        flask_thread = threading.Thread(target=start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        webbrowser.open("http://127.0.0.1:5000")
        while not token_info:
            token_info = get_token_info()
            time.sleep(1)

    if is_token_expired(token_info):
        print("Access token has expired. Refreshing...")
        token_info = refresh_access_token(token_info)

    if test_access_token(token_info):
        print("Access token is valid.")
        track_id = "0R8JLNP107Hr7V7lL9oh13"  # Example track ID
        audio_feature = fetch_audio_feature(token_info, track_id)
        if audio_feature:
            print("Audio feature fetched successfully:")
            print(audio_feature)
    else:
        print("Failed to validate access token.")

if __name__ == "__main__":
    main()