"""
    This module holds the login routines for the Spotify API
"""

# Standard library imports
import os
from typing import Any
from typing import Callable
from functools import wraps

# Third party imports
from dotenv import load_dotenv
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyOAuth

# Local imports
from .classes import ExtendedSpotify

# Main body
def login(scope: str) -> ExtendedSpotify:
    """Log in to the Spotify API

    Args:
        scope (str): Scope for the connection

    Returns:
        ExtendedSpotify: Spotify object
    """

    env_values = dotenv_values(".env")  # Load environment variables

    sp_oauth = SpotifyOAuth(
        client_id=env_values.get("SPOTIPY_CLIENT_ID"),
        client_secret=env_values.get("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=env_values.get("SPOTIPY_REDIRECT_URI"),
        scope=scope,
    )

    return ExtendedSpotify(auth_manager=sp_oauth)


def login_if_missing(scope: str) -> Callable[[Callable[[ExtendedSpotify], Any]], Any]:
    def decorator(func):
        @wraps(func)
        def wrapper(sp=None, **kwargs):
            if sp is None:
                sp = login(scope=scope)
            rv = func(sp, **kwargs)
            return rv

        return wrapper

    return decorator
