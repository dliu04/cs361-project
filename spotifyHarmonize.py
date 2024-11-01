import os
import authorize
import threading
import webbrowser
import time
import requests
import spotipy
import json

def run_flask():
    authorize.app.run(port=5000)

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def playlist_input():
    # Get the playlist ID from the user
    playlist_url = input("Enter the playlist URL: ")
    playlist_id = playlist_url.split('/')[-1]
    print("Playlist ID:", playlist_id)
    return playlist_id

def user_top_5_songs():
    try:
        # Read the token info from the file
        with open('token_info.json', 'r') as f:
            token_info = json.load(f)
    except FileNotFoundError:
        print('User not logged in')
        return

    # Create a Spotipy instance with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Get the user's top tracks
    top_tracks = sp.current_user_top_tracks(limit=5)['items']

    # Display the top 5 tracks
    print("Your Top 5 Songs:")
    for idx, track in enumerate(top_tracks):
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")


def main():
    while True:
        print("Welcome to Spotify Harmonize!")
        print("This software will generate a recommended playlist inspired by a playlist of your choosing.")
        print("Please ensure the intended playlists are public before you begin.")
        print("\n")
        print("1. Login to Spotify")
        print("2. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            # Start the Flask app in a new thread
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()

            # Wait a moment for the server to start
            time.sleep(2)

            # Open the Spotify login page
            webbrowser.open("http://127.0.0.1:5000")

            # Create a session for requests to maintain cookies
            session = requests.Session()

            # Check if authorized
            while True:
                response = session.get("http://127.0.0.1:5000/savePlaylist")
                if response.text == "OAUTH SUCCESSFUL! You can now generate playlists.":
                    print("Authorization successful!")
                    break

            # Now check the savePlaylist response
            # save_playlist_response = session.get("http://127.0.0.1:5000/savePlaylist")
           # print(save_playlist_response.text)  # This will show "OAUTH SUCCESSFUL! You can now generate playlists."

            time.sleep(1)
             # clear_screen()

            user_top_5_songs()

        elif choice == '2':
            print("Harmonize next time!")
            break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()
