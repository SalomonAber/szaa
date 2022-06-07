import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import g, current_app


def get_sp():
    if "sp" not in g:
        g.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=current_app.config["SPOTIFY_CLIENT_ID"],
                client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
            )
        )

    return g.sp


def init_sp():
    sp = get_sp()
