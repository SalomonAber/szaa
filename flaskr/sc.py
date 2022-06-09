from __future__ import annotations
from flask import g, current_app
from typing import Any
import requests


class Soundcloud:
    def __init__(self, base_url: str, client_id: str) -> Soundcloud:
        """
        Initialise instance
        Parameters
        ----------
        `self` : Self-explanatory
        `base_url` : The base url of the Soundcloud API
        `client_id` : The client ID used to authenticate each request
        """
        self.client_id = client_id
        self.base_url = base_url

    def get_tracks(self: Any, user_id: str) -> list[dict]:
        """
        Get a list of tracks owned by a user
        Parameters
        ----------
        `self` : Self-explanatory
        `user_id` : The tracks' user ID of the owner
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
        }
        response = requests.get(
            "{}/users/{}/tracks".format(
                self.base_url,
                user_id,
            ),
            params={"client_id": self.client_id},
            headers=headers,
        )
        if response.status_code != 200:
            raise Exception("{} {}".format(response.status_code, response.reason))
        return response.json()


def get_sc():
    if "sc" not in g:
        g.sc = Soundcloud(
            base_url=current_app.config["SOUNDCLOUD_BASE_URL"],
            client_id=current_app.config["SOUNDCLOUD_CLIENT_ID"],
        )

    return g.sc


def get_tracks():
    tracks = []
    try:
        sc = get_sc()
        data = sc.get_tracks(current_app.config["SOUNDCLOUD_USER_ID"])
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
                current_app.logger.error("Error loading track '%s': %s", sc_track, err)
    except Exception as err:
        current_app.logger.error("Error loading sc: %s", err)
    return tracks
