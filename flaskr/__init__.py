import os
from . import sp
from flaskr.sp import get_sp
from flask import Flask, render_template, g


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

    with app.app_context():
        sp.init_sp()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/music")
    def music():
        with app.app_context():
            sp = get_sp()
            playlists = []
            user_playlists = []
            result = sp.user_playlists(app.config["SPOTIFY_USER_ID"])
            if "items" in result:
                user_playlists = result["items"]
            for user_playlist in user_playlists:
                playlist = {}
                try:
                    playlist["name"] = user_playlist["name"]
                    playlist["href"] = user_playlist["external_urls"]["spotify"]
                    srcset = []
                    for image in user_playlist["images"]:
                        if image["width"] is None:
                            image["width"] = 300
                        srcset += ["{} {}x".format(image["url"], image["width"] / 300)]
                        if image["width"] == 300:
                            playlist["src"] = image["url"]
                    playlist["srcset"] = ", ".join(srcset)
                    playlists += [playlist]
                except Exception as err:
                    print(
                        "Error loading playlist {}: {}".format(
                            user_playlist["name"], err
                        )
                    )
            return render_template("music.html", playlists=playlists)

    return app
