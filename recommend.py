import json
import requests
import spotipy

from shared import clear_screen

#I want it so that depending on user input, it either passes the playlist tracks or top five tracks
# to recommend songs

def get_playlist_seed(playlist_id):
    # Clear the console screen
    clear_screen()
    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)
    # Create a Spotipy instance with the access token
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
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Get the user's top tracks for the past month
    top_tracks = sp.current_user_top_tracks(time_range='short_term', limit=5)['items'] # short_term (4 weeks), medium_term (6 months), long_term (past year)
    # List the user's top tracks:
    print("Your top tracks for the past month:")
    for idx, track in enumerate(top_tracks):
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")
    # Extract the track IDs
    seed_tracks = [track['id'] for track in top_tracks]
    # Return tracks
    return seed_tracks

def recommend_songs(seed_tracks):
    # Get the token info from the file
    with open('token_info.json', 'r') as f:
        token_info = json.load(f)
    # Create a Spotipy instance with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Get the audio features for the tracks
    audio_features = sp.audio_features(seed_tracks)
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