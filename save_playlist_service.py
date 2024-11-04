from flask import Flask, request, jsonify  
import spotipy  
import json  

app = Flask(__name__) 

@app.route('/save_playlist', methods=['POST'])  # Define a route for saving playlists, accepting POST requests
def save_playlist():
    data = request.json  # Get the JSON data from the request
    token_info = data['token_info']  # Extract token information from the request data
    playlist_name = data['playlist_name']  # Extract the playlist name from the request data
    track_ids = data['track_ids']  # Extract the track IDs from the request data

    sp = spotipy.Spotify(auth=token_info['access_token'])  # Create a Spotipy client with the access token
    user_id = sp.current_user()['id']  # Get the current user's ID
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)  # Create a new private playlist for the user
    sp.user_playlist_add_tracks(user_id, playlist['id'], track_ids)  # Add tracks to the newly created playlist

    return jsonify({"message": "Playlist saved successfully!"}), 200  # Return a success message as JSON with a 200 status code

if __name__ == "__main__":
    app.run(port=5001, debug=False)  # Run the Flask application on port 5001 with debug mode off