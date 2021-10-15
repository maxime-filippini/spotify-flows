import os
from dotenv import load_dotenv
from contextlib import contextmanager
from functools import wraps

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify.classes import ExtendedSpotify


@contextmanager
def login(scope: str) -> ExtendedSpotify:
    try:
        load_dotenv()

        sp_oauth = SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
            scope=scope,
        )

        access_token = ""
        token_info = sp_oauth.get_cached_token()

        if token_info:
            access_token = token_info["access_token"]
        else:
            auth_url = sp_oauth.get_authorize_url()
            print(auth_url)
            response = input(
                "Paste the above link into your browser, then paste the redirect url here: "
            )

            code = sp_oauth.parse_response_code(response)
            token_info = sp_oauth.get_access_token(code)

            access_token = token_info["access_token"]

        yield ExtendedSpotify(auth=access_token)

    finally:
        pass


def autologin(scope: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with login(scope=scope) as sp:
                rv = func(sp, *args, **kwargs)
            return rv

        return wrapper

    return decorator
