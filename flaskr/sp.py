import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import math
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


def get_playlists():
    playlists = []
    try:
        sp = get_sp()
        data = sp.user_playlists(current_app.config["SPOTIFY_USER_ID"], limit=20)
        if "items" not in data:
            raise Exception("JSON response invalid")
        sp_playlist = data["items"]
        for sp_playlist in sp_playlist:
            playlist = {}
            try:
                playlist["name"] = sp_playlist["name"]
                playlist["href"] = sp_playlist["external_urls"]["spotify"]
                srcset = []
                distance = math.inf
                closest = None
                for image in sp_playlist["images"]:
                    # Custom images do not have width property
                    # If closest is None accept custom image
                    if image["height"] is None and closest is None:
                        closest = image
                        continue
                    if abs(image["height"] - 300) < distance:
                        distance = abs(image["height"] - 300)
                        closest = image
                if closest is None:
                    raise Exception("No suitable thumbnail exists")
                playlist["src"] = closest["url"]
                for image in sp_playlist["images"]:
                    if image["height"] is None:
                        continue
                    srcset += [
                        "{} {}x".format(
                            image["url"], image["height"] / closest["height"]
                        )
                    ]
                playlist["srcset"] = ", ".join(srcset)
                playlists += [playlist]
            except Exception as err:
                current_app.logger.error(
                    "Error loading playlist '%s': %s", sp_playlist["name"], err
                )
    except Exception as err:
        current_app.logger.error("Error loading playlists: %s", err)
    return playlists
