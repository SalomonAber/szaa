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
