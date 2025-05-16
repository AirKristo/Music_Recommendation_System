# How to run the code:
# python spotify_api.py <file_path> <start_index> <end_index> <client_id> <client_secret>
# Example:
# python spotify_api.py 4000_playlists_91598.csv 0 100 SPOTIFY_CLIENT_ID SPOTIFY_CLIENT_SECRET

import pandas as pd
import spotipy
import argparse
import os
import base64
import requests
import time
from numexpr.necompiler import context_info


# Function to initialize Spotify API Client
def initialize_spotify_client(client_id, client_secret):
    # Base64 encoded credentials
    client_credentials = f"{client_id}:{client_secret}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode())
    
    # Request the access token
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {client_credentials_base64.decode()}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data, headers=headers)
    
    if response.status_code == 200:
        access_token = response.json()['access_token']
        print("Access token obtained successfully.")
        return spotipy.Spotify(auth=access_token)
    else:
        print("Error obtaining access token.")
        exit()

def read_csv_subset(file_path, start_index, end_index):
    # Load the CSV and select the subset of the data
    df = pd.read_csv(file_path)
    subset_df = df.iloc[int(start_index):int(end_index)]
    return subset_df

def get_unique_track_ids(subset_df):
    # Extract unique track IDs
    track_ids = subset_df["track_id"].unique().tolist()
    return track_ids

def fetch_track_info_in_batches(spotify_client, track_ids, batch_size=50):
    # Container for storing track information
    tracks_data = []

    #Put tracks into batches
    for i in range(0, len(track_ids), batch_size):
        batch_ids = track_ids[i:i + batch_size]

        try:
            track_info = spotify_client.tracks(batch_ids)
            audio_features = spotify_client.audio_features(batch_ids)
        except Exception as e:
            print(f"Error fetching batch {i}-{i + batch_size}: {e}")
            continue

        for track, audio_feature in zip(track_info["tracks"], audio_features):
            if not audio_feature:
                continue
            tracks_data.append({
                "Track_ID": track["id"],
                "Popularity": track.get("popularity"),
                "Release Date": track.get("album", {}).get("release_date"),
                "Explicit": track.get("explicit"),
                "External URLs": track.get("external_urls", {}).get("spotify"),
                "Danceability": audio_feature.get("danceability"),
                "Energy": audio_feature.get("energy"),
                "Key": audio_feature.get("key"),
                "Loudness": audio_feature.get("loudness"),
                "Mode": audio_feature.get("mode"),
                "Speechiness": audio_feature.get("speechiness"),
                "Acousticness": audio_feature.get("acousticness"),
                "Instrumentalness": audio_feature.get("instrumentalness"),
                "Liveness": audio_feature.get("liveness"),
                "Valence": audio_feature.get("valence"),
                "Tempo": audio_feature.get("tempo")
            })
    
    return pd.DataFrame(tracks_data)

def main(file_path, start_index, end_index, client_id, client_secret):
    # Step 1: Read the CSV and process the subset
    subset_df = read_csv_subset(file_path, start_index, end_index)
    
    # Step 2: Get the list of unique track IDs
    track_ids = get_unique_track_ids(subset_df)
    
    # Step 3: Fetch track information using Spotify API
    spotify_client = initialize_spotify_client(client_id, client_secret)
    track_info_df = fetch_track_info_in_batches(spotify_client, track_ids)
    
    # Step 4: Save the output to CSV
    output_file = f"{start_index}_{end_index}.csv"
    track_info_df.to_csv(output_file, index=False)
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Spotify tracks information from CSV")
    parser.add_argument("file_path", type=str, help="Path to the input CSV file")
    parser.add_argument("start_index", type=int, help="Start index of the subset")
    parser.add_argument("end_index", type=int, help="End index of the subset")
    parser.add_argument("client_id", type=str, help="Spotify API client ID")
    parser.add_argument("client_secret", type=str, help="Spotify API client secret")
    
    args = parser.parse_args()
    main(args.file_path, args.start_index, args.end_index, args.client_id, args.client_secret)
