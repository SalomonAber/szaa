import os
from turtle import width
from flaskr.sp import get_sp
from flaskr.sc import get_sc
from flaskr.yt import get_yt
from flask import Flask, render_template
from flask_caching import Cache
import math


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path="",
        static_folder="static",
        template_folder="templates",
    )

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cache = Cache(app)

    @app.route("/")
    @cache.cached()
    def index():
        return render_template("index.html")

    @app.route("/music")
    # @cache.cached()
    def music():
        with app.app_context():
            # Soundcloud
            tracks = []
            try:
                sc = get_sc()
                data = sc.get_tracks(app.config["SOUNDCLOUD_USER_ID"])
                if "collection" not in data:
                    raise Exception("JSON response invalid")
                sc_tracks = data["collection"]
                for sc_track in sc_tracks:
                    track = {}
                    try:
                        track["id"] = sc_track["id"]
                        track["name"] = sc_track["title"]
                        track["href"] = sc_track["permalink_url"]
                        track["src"] = sc_track["artwork_url"]
                        tracks += [track]
                    except Exception as err:
                        app.logger.error("Error loading track '%s': %s", sc_track, err)
            except Exception as err:
                app.logger.error("Error loading tracks: %s", err)
            # Spotify
            playlists = []
            try:
                sp = get_sp()
                data = sp.user_playlists(app.config["SPOTIFY_USER_ID"], limit=20)
                if "items" not in data:
                    raise Exception("JSON response invalid")
                sp_playlists = data["items"]
                for sp_playlist in sp_playlists:
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
                        app.logger.error(
                            "Error loading playlist '%s': %s", sp_playlist["name"], err
                        )
            except Exception as err:
                app.logger.error("Error loading playlists: %s", err)
            # Youtube
            ntdbs = []
            try:
                yt = get_yt()
                request = yt.playlistItems().list(
                    part="snippet",
                    playlistId=app.config["NPR_TINY_DESK_BEST_ID"],
                    maxResults=20,
                )
                response = request.execute()
                yt_items = response["items"]
                for yt_item in yt_items:
                    ntdb = {}
                    try:
                        ntdb["name"] = yt_item["snippet"]["title"]
                        ntdb[
                            "href"
                        ] = "https://www.youtube.com/watch?v={}&list={}".format(
                            yt_item["snippet"]["resourceId"]["videoId"],
                            yt_item["snippet"]["playlistId"],
                        )
                        srcset = []
                        distance = math.inf
                        closest = None
                        for image in yt_item["snippet"]["thumbnails"].values():
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
                        ntdb["src"] = closest["url"]
                        for image in yt_item["snippet"]["thumbnails"].values():
                            if image["height"] is None:
                                continue
                            srcset += [
                                "{} {}x".format(
                                    image["url"], image["height"] / closest["height"]
                                )
                            ]
                        ntdb["srcset"] = ", ".join(srcset)
                        ntdbs += [ntdb]
                    except Exception as err:
                        app.logger.error(
                            "Error loading ntdb '%s': %s",
                            yt_item["snippet"]["title"],
                            err,
                        )
            except Exception as err:
                app.logger.error("Error loading ntdbs: %s", err)
            return render_template(
                "music.html", tracks=tracks, playlists=playlists, ntdbs=ntdbs
            )

    @app.route("/food")
    # @cache.cached()
    def food():
        return render_template("food.html")

    @app.route("/photography")
    # @cache.cached()
    def photography():
        return render_template("photography.html")

    return app
