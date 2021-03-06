import os
from flask import Flask, session, request, redirect, render_template, abort, jsonify, Blueprint
from flask_session import Session
import spotipy
import uuid
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import random
import json
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

blueprint = Blueprint("api", __name__, url_prefix="/api")


api = Api(blueprint, doc="/doc/")
app.register_blueprint(blueprint)
print(app.url_map)

# load model
kmeans = joblib.load("ml/model/kmeans.joblib")
scaler = joblib.load("ml/model/scaler.joblib")

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route("/")
def index():
    # assume user has authenticated
    auth = {
        "has_auth": True
    }

    if not session.get('uuid'):
        # visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    # create auth manager
    cache_handler = spotipy.cache_handler.CacheFileHandler(
        cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-top-read user-modify-playback-state user-read-playback-state',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        auth["auth_url"] = auth_url
        auth["has_auth"] = False
        return render_template("index.html", auth=auth)

    # signed in, display page
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    print(spotify)
    return render_template("index.html", spotify=spotify, auth=auth)


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/select_song')
def select_song():
    # assume user has authenticated
    auth = {
        "has_auth": True
    }
    return render_template("select_song.html", auth=auth)


def handle_auth():
    cache_handler = spotipy.cache_handler.CacheFileHandler(
        cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify


@api.route('/playlists')
class Playlists(Resource):
    def get(self):
        spotify = handle_auth()
        return spotify.current_user_playlists()


@api.route('/top_tracks')
class TopTracks(Resource):
    def get(self):
        spotify = handle_auth()
        top_tracks = spotify.current_user_top_tracks(
            limit=50, offset=0, time_range="short_term")
        return top_tracks


@api.route('/analyse_top_tracks')
class AnalyseTopTracks(Resource):
    def get(self):
        spotify = handle_auth()
        # tracks
        my_tracks = []
        topTracks = TopTracks()
        top_tracks = topTracks.get()["items"]
        # get track ids
        for track in top_tracks:
            my_tracks.append({
                "id": track["id"],
                "name": track["name"]
            })
        # get track features
        track_features = spotify.audio_features(
            [track["id"] for track in my_tracks])

        features = []
        for track in track_features:
            features.append([
                track["acousticness"],
                track["danceability"],
                track["duration_ms"],
                track["energy"],
                track["instrumentalness"],
                track["key"],
                track["liveness"],
                track["loudness"],
                track["speechiness"],
                track["tempo"],
                track["valence"]
            ])

        scaled_features = scaler.transform(features)
        labels = kmeans.predict(scaled_features)
        label_count = {}
        for label in labels:
            if str(label) in label_count.keys():
                label_count[str(label)] += 1
            else:
                label_count[str(label)] = 1
        return label_count


@api.route('/devices')
class Devices(Resource):
    def get(self):
        spotify = handle_auth()
        devices = spotify.devices()
        return devices


@api.route('/select_top_song')
class TopSong(Resource):
    def get(self):
        spotify = handle_auth()
        # logic
        analyseTopTracks = AnalyseTopTracks()
        label_count = analyseTopTracks.get()
        choice = random.choices(
            list(label_count), list(label_count.values()), k=1)

        all_tracks_labeled = pd.read_csv("ml/data/spotify_data_labeled.csv")
        filtered_tracks = all_tracks_labeled[(all_tracks_labeled["label"] == int(
            choice[0]))]
        selected_track = random.choices(filtered_tracks["id"].values.tolist(
        ), filtered_tracks["popularity"].values.tolist())

        track_info = spotify.track(selected_track[0])

        spotify.start_playback(uris=[track_info["uri"]])

        return track_info


@api.route('/currently_playing')
class CurrentlyPlaying(Resource):
    def get(self):
        spotify = handle_auth()
        track = spotify.current_user_playing_track()
        if track is not None:
            return track
        return {"is_playing": False}


@api.route('/current_user')
class CurrentUser(Resource):
    def get(self):
        spotify = handle_auth()
        return spotify.current_user()


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get(
        "PORT", os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))
