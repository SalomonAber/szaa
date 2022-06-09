from flaskr.sp import get_playlists
from flaskr.sc import get_tracks
from flaskr.yt import get_videos
from flaskr.r import get_r
from flask import Flask, render_template, jsonify
from flask_caching import Cache
import json


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

    cache = Cache(app)

    @app.route("/trigger")
    def trigger():
        """
        Load API data into Reddis
        """
        with app.app_context():
            r = get_r()
            # Soundcloud
            tracks = get_tracks()
            json_sc = json.dumps(tracks)
            r.set("sc", json_sc)
            # Spotify
            playlists = get_playlists()
            json_sp = json.dumps(playlists)
            r.set("sp", json_sp)
            # Youtube
            videos = get_videos()
            json_yt = json.dumps(videos)
            r.set("yt", json_yt)
            return jsonify(success=True)

    @app.route("/")
    @cache.cached()
    def index():
        return render_template("index.html")

    @app.route("/music")
    @cache.cached()
    def music():
        with app.app_context():
            r = get_r()
            tracks = []
            json_sc = r.get("sc")
            if json_sc is not None:
                tracks = json.loads(json_sc.decode("utf-8"))
            playlists = []
            json_sp = r.get("sp")
            if json_sp is not None:
                playlists = json.loads(json_sp.decode("utf-8"))
            videos = []
            json_yt = r.get("yt")
            if json_yt is not None:
                videos = json.loads(json_yt.decode("utf-8"))
            return render_template(
                "music.html", tracks=tracks, playlists=playlists, videos=videos
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
