import os
import spotipy
import spotipy.util as util
import string
import random
import requests
import datetime
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import base64
import pandas as pd
import pytz

os.environ['SPOTIPY_CLIENT_ID']='f7a43754c96842d0abe4714b5d46b5b8'
os.environ['SPOTIPY_CLIENT_SECRET']='b220dc8a84284d15960df4b2460255ee'
os.environ['SPOTIPY_REDIRECT_URI']='http://127.0.0.1:8000/'

def get_token():
    scope=['user-library-read','user-read-recently-played','playlist-modify-private','playlist-modify-public','playlist-read-private','playlist-read-collaborative','user-read-private']
    client_id = "7642a65ef65a412c98d59a91d0acf35a"
    client_secret = "db2c940d8cd9495592bb9f8e2d9237c9"
    redirect_uri = "http://localhost:8888/callback/"
    auth_obj = SpotifyOAuth(scope = scope, client_id = "7642a65ef65a412c98d59a91d0acf35a", client_secret = "db2c940d8cd9495592bb9f8e2d9237c9", redirect_uri = "http://localhost:8888/callback/")
    auth_code = auth_obj.get_auth_response()
    print(auth_code)
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{client_id}:{client_secret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')


    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "authorization_code"
    data['code'] = auth_code
    data["redirect_uri"] = redirect_uri
    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    token = r.json()["access_token"]
    if token:
        return token
    else:
        print("Can't find user token. Try again")

def fetch_username(token):
    uri = '	https://api.spotify.com/v1/me'
    req = requests.get(uri,headers={'Authorization': 'Bearer ' + str(token)})
    req = req.json()
    print(req)
    username = req['id']
    return username


def fetch_ids(token):
    if token:
        # print(token)
        # sp = spotipy.Spotify(auth=token)
        # sp.trace = False
        # results = sp.current_user_playlists(limit=50)
        # for i, item in enumerate(results['items']):
        #     print("%d %s" %(i, item['name']))
        # #user history
        uri = 'https://api.spotify.com/v1/me/player/recently-played'
        req = requests.get(uri,headers={'Authorization': 'Bearer ' + str(token)},params={'limit':50})
        data = req.json()
        ids = [data['items'][i]['track']['id'] for i in range(len(data['items']))]
        return ids
    else:
        print("Can't fetch user history")
        return []

def create_playlist(token, ids):
    username = fetch_username(token)
    sp = spotipy.Spotify(auth=token)
    IST = pytz.timezone('Asia/Kolkata')
    time = datetime.datetime.now(IST)
    playlist_name = f'Playlist by Moodify | {time.strftime(f"%m/%d/%Y, %H:%M:%S")}'   
    sp.user_playlist_create(username, name=playlist_name)
    print("Successfully created Playlist")
    
    playlist_id = ''
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:  # iterate through playlists I follow
        if playlist['name'] == playlist_name:  # filter for newly created playlist
            playlist_id = playlist['id']

    sp.user_playlist_add_tracks(username, playlist_id, ids)
    return None

def make_df(token):
    
    auth_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))

    sp=spotipy.Spotify(auth_manager=auth_manager)
    ids=fetch_ids(token)
    df = pd.DataFrame(columns=['ID', 'Name', 'Album', 'Artist', 'Release_date', 'Popularity', 'Acousticness', 'Danceability', 'Energy',
                                        'Instrumentalness', 'Liveness', 'Loudness',
                                        'Speechiness', 'Tempo', 'Time_signature', 'Valence', 'Length', 'Key', 'Mode'])
                                        
    for id in ids:
        track_info= sp.track(id)
        track_features = sp.audio_features(id)
        name= track_info['name']
        album = track_info['album']['name']
        artist = track_info['album']['name']
        release_date = track_info['album']['release_date']
        popularity= track_info['popularity']
        acousticness = track_features[0]['acousticness']
        danceability= track_features[0]['danceability']
        energy= track_features[0]['energy']
        instrumentalness= track_features[0]['instrumentalness']
        liveness= track_features[0]['liveness']
        loudness= track_features[0]['loudness']
        speechiness= track_features[0]['speechiness']
        tempo= track_features[0]['tempo']
        time_signature= track_features[0]['time_signature']
        valence= track_features[0]['valence']
        length= track_features[0]['duration_ms']
        key= track_features[0]['key']
        mode= track_features[0]['mode']
        track=[name, album, artist, release_date, popularity, acousticness,
            danceability, energy, instrumentalness, liveness, loudness,
            speechiness,tempo, time_signature, valence, length, key, mode]
        track
        df = df.append({
                        'ID': id, 'Name':name, 'Album':album, 'Artist':artist, 'Release_date':release_date, 'Popularity':popularity,
                        'Acousticness':acousticness, 'Danceability':danceability, 'Energy':energy,
                                            'Instrumentalness':instrumentalness, 'Liveness':liveness, 'Loudness':loudness,
                                            'Speechiness':speechiness, 'Tempo':tempo, 'Time_signature':time_signature, 'Valence':valence,
                        'Length':length, 'Key': key, 'Mode':mode
                        }
                        ,ignore_index=True
                        )
    print(df)
    return df

if __name__ == "__main__":
    token = get_token()
    print(fetch_ids(token))
    print(token)

    