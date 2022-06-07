import googleapiclient.discovery
from flask import g, current_app


def get_yt():
    if "yt" not in g:
        g.yt = googleapiclient.discovery.build(
            "youtube",
            "v3",
            developerKey=current_app.config["YOUTUBE_API_KEY"],
        )

    return g.yt
