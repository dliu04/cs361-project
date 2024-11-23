import os
import authorize
import threading
import webbrowser
import time
import spotipy
import json

# From other Python files
from shared import *
from recommend import *

def run_flask():
    authorize.app.run(port=5000)

def is_authorized():
    if not os.path.exists('token_info.json'):
        return False

    with open('token_info.json', 'r') as f:
        token_info = json.load(f)

    if 'access_token' not in token_info:
        return False

    return True

def playlist_input():
    while True:
        # Clear the screen
        clear_screen()

        # Get the playlist URL from the user
        print("Please paste your playlist URL.")
        print("Ensure that your account has access to this playlist, as the program will attempt to access songs from it.")
        print("You may also enter 'q' to quit.\n")
        playlist_url = input("Enter the playlist URL: ")
        
        if playlist_url.lower() == 'q':
            return 'quit'
        
        # Extract the playlist ID from the URL
        if 'playlist' in playlist_url:
            playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
            return playlist_id
        else:
            print("Invalid playlist URL. Please try again.")

def new_or_recommend(playlist_id):    
    while True:
        # Clear the screen
        clear_screen()

        # Get the token info from the file
        with open('token_info.json', 'r') as f:
            token_info = json.load(f)

        # Create a Spotipy instance with the access token
        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Fetch the playlist details
        playlist_details = sp.playlist(playlist_id)

        # Extract the playlist name
        playlist_name = playlist_details['name']

        # Explanation
        print("You can choose to select a different playlist to recommend songs from,\nor recommend songs based on your currently selected playlist.\n")

        # Display the options
        print("The selected playlist is:", playlist_name)
        print("1. Select new playlist")
        print("2. Recommend Songs")
        print("3. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            return None  # Indicate that we need to select a new playlist
        elif choice == '2':
            seed_tracks = get_playlist_seed(playlist_id)
            recommend_songs(seed_tracks)
        elif choice == '3':
            return 'quit'
        else:
            print("Invalid input. Please try again.")


# To clean up temporary files
import atexit
import shutil

def cleanup():
    # List of folders to delete
    temp_folders = ['__pycache__', 'flask_session']
    for folder in temp_folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)

def recommend_based_on_playlist():
    while True:
        playlist_id = playlist_input()
        if playlist_id == 'quit':
            break
        if playlist_id:
            result = new_or_recommend(playlist_id)
            if result == 'quit':
                break

def recommend_based_on_top_five():
    seed_tracks = get_top_tracks()
    recommend_songs(seed_tracks)

def main():
    # Clear the console screen
    clear_screen()

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
            time.sleep(1)

            # Open the Spotify login page
            webbrowser.open("http://127.0.0.1:5000")

            # Wait until the user is authorized
            while not is_authorized():
                time.sleep(0.1)

            time.sleep(1)
            clear_screen()

            print("What would you like to do?")
            print("1. Recommend songs based on a playlist")
            print("2. Recommend songs based on top five songs in the past month")
            recommendChoice = input("Enter your choice: ")
            if recommendChoice == '1':
                recommend_based_on_playlist()
            elif recommendChoice == '2':
                recommend_based_on_top_five()
            break
        elif choice == '2':
            break
        else:
            print("Invalid input. Please try again.")
    
    if os.path.exists('token_info.json'):
            os.remove('token_info.json')
    
    if os.path.exists('.cache'):
        os.remove('.cache')

    print("Harmonize next time!")
    
atexit.register(cleanup)

if __name__ == "__main__":
    main()
