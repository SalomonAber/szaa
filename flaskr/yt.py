import googleapiclient.discovery
import math
from flask import g, current_app


def get_yt():
    if "yt" not in g:
        g.yt = googleapiclient.discovery.build(
            "youtube",
            "v3",
            developerKey=current_app.config["YOUTUBE_API_KEY"],
        )

    return g.yt


def get_videos():
    videos = []
    try:
        yt = get_yt()
        request = yt.playlistItems().list(
            part="snippet",
            playlistId=current_app.config["NPR_TINY_DESK_BEST_ID"],
            maxResults=20,
        )
        response = request.execute()
        yt_videos = response["items"]
        for yt_video in yt_videos:
            video = {}
            try:
                video["name"] = yt_video["snippet"]["title"]
                video["href"] = "https://www.youtube.com/watch?v={}&list={}".format(
                    yt_video["snippet"]["resourceId"]["videoId"],
                    yt_video["snippet"]["playlistId"],
                )
                srcset = []
                distance = math.inf
                closest = None
                for image in yt_video["snippet"]["thumbnails"].values():
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
                video["src"] = closest["url"]
                for image in yt_video["snippet"]["thumbnails"].values():
                    if image["height"] is None:
                        continue
                    srcset += [
                        "{} {}x".format(
                            image["url"], image["height"] / closest["height"]
                        )
                    ]
                video["srcset"] = ", ".join(srcset)
                videos += [video]
            except Exception as err:
                current_app.logger.error(
                    "Error loading ntdb '%s': %s",
                    yt_video["snippet"]["title"],
                    err,
                )
    except Exception as err:
        current_app.logger.error("Error loading ntdbs: %s", err)
    return videos
