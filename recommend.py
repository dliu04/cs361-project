import json
import requests
import spotipy
import time

from shared import *
from authorize import create_spotify_oauth

#I want it so that depending on user input, it either passes the playlist tracks or top five tracks
# to recommend songs

def get_playlist_seed(playlist_id):
    # Clear the console screen
    clear_screen()
    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)
    # Create a Spotipy instance with the access token
    print(f"Access token: {token_info['access_token']}")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Get the playlist tracks
    playlist_tracks = sp.playlist_tracks(playlist_id)['items']
    # Extract the track IDs
    track_ids = [track['track']['id'] for track in playlist_tracks if track['track'] is not None]
    # Ensure we have at most 5 seed tracks (Spotify API limit)
    seed_tracks = track_ids[:5]
    # Return tracks
    return seed_tracks

def get_top_tracks():
    # Clear the console screen
    clear_screen()
    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)
    # Create a Spotipy instance with the access token
    print(f"Access token: {token_info['access_token']}")
    sp = spotipy.Spotify(auth=token_info['access_token'])

    print("Select a time frame:")
    print("1. Past month")
    print("2. Past 6 months")
    print("3. Past year")
    choice = input("Enter your choice: ")

    if choice == '1':
        term_range = 'short_term'
    elif choice == '2':
        term_range = 'medium_term'
    elif choice == '3':
        term_range = 'long_term'
    else:
        print("Invalid choice!")
        return

    # Get the user's top tracks for the past month
    top_tracks = sp.current_user_top_tracks(time_range=term_range, limit=5)['items'] # short_term (4 weeks), medium_term (6 months), long_term (past year)
    # List the user's top tracks:
    print("Your top tracks for the selected range: ")
    for idx, track in enumerate(top_tracks):
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")
    # Extract the track IDs
    seed_tracks = [track['id'] for track in top_tracks]
    # Return tracks
    return seed_tracks

def recommend_songs(seed_tracks):
    # Clear the console screen
    clear_screen()
    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)
    
    print("Got the token file!")
    input()

    # Create a Spotipy instance with the access token
    print(f"Access token: {token_info['access_token']}")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    print("Created spotipy instance!")
    input()

    # Check if the token has expired
    if token_info['expires_at'] - int(time.time()) < 60:
        print("Token has expired, refreshing...")
        input()
        token_info = create_spotify_oauth().refresh_access_token(token_info['refresh_token'])
        with open('token_info.json', 'w') as f:
            json.dump(token_info, f)
        print(f"New access token: {token_info['access_token']}")
        sp = spotipy.Spotify(auth=token_info['access_token'])
    else:
        print("Token has not expired!")
        print(f"Token scopes: {token_info.get('scope')}")
        input()

    # Check for any rate limit issues
    try:
        sp.audio_features(seed_tracks)
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get('Retry-After', 1))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            sp = spotipy.Spotify(auth=token_info['access_token'])
        else:
            print(f"SpotifyException: HTTP status: {e.http_status}, Code: {e.code}, Reason: {e.reason}")
            print(f"Response headers: {e.headers}")
            raise e
        
    

    print("Getting audio features...")
    input()

    try:
        audio_features = sp.audio_features(seed_tracks)
    except spotipy.exceptions.SpotifyException as e:
        print(f"SpotifyException: HTTP status: {e.http_status}, Code: {e.code}, Reason: {e.reason}")
        print(f"Response headers: {e.headers}")
        raise e

    print("Got audio features!")
    input()


    # Extract the audio features
    features = [track for track in audio_features if track is not None]
    # Calculate the average audio features
    avg_features = {}
    for feature in features:
        for key, value in feature.items():
            if isinstance(value, (int, float)):  # Ensure the value is numeric
                if key in avg_features:
                    avg_features[key] += value
                else:
                    avg_features[key] = value
    for key in avg_features:
        avg_features[key] /= len(features)
    # Get the recommended tracks based on the average audio features
    recommendations = sp.recommendations(
        seed_tracks=seed_tracks, 
        limit=99, 
        target_acousticness=avg_features.get('acousticness', 0),
        target_danceability=avg_features.get('danceability', 0),
        target_energy=avg_features.get('energy', 0),
        target_instrumentalness=avg_features.get('instrumentalness', 0),
        target_liveness=avg_features.get('liveness', 0),
        target_valence=avg_features.get('valence', 0)
    )

    # Define track_ids before using it
    track_ids = seed_tracks

    # Filter out tracks that are already in the playlist
    recommended_tracks = [track for track in recommendations['tracks'] if track['id'] not in track_ids]
    # Display the recommended tracks
    print("Recommended Songs:")
    for idx, track in enumerate(recommended_tracks):
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")

    ### Save the recommended tracks to a new playlist

    # Get user input
    print("\nWould you like to save the recommended songs to a new playlist?")
    print("1. Yes")
    print("2. No")
    choice = input("Enter your choice: ")

    if choice == '1':
        # Clear the screen
        clear_screen()
        # Send the recommended tracks to the microservice
        playlist_name = input("Enter the name of the new playlist: ")
        track_ids = [track['id'] for track in recommended_tracks]
        response = requests.post("http://127.0.0.1:5001/save_playlist", json={
            "token_info": token_info,
            "playlist_name": playlist_name,
            "track_ids": track_ids
        })
        if response.status_code == 200:
            print("Playlist saved successfully!")
        else:
            print("Failed to save playlist.")
    elif choice == '2':
        pass
    else:
        print("Invalid input!")
    
    input("\nPress Enter to continue...")