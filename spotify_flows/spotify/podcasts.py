"""
    This module holds the API functions related to podcast information
"""

# Standard library imports
from typing import Any
from typing import List
from typing import Dict
from typing import Union
from pathlib import Path

# Third party imports
import yaml

# Local imports
from .login import login_if_missing
from .classes import ExtendedSpotify
from .playlists import wipe_playlist
from .playlists import get_playlist_id
from .data_structures import EpisodeItem

# Main body
@login_if_missing(scope="user-read-playback-position")
def read_show_from_id(sp: ExtendedSpotify, *, show_id: str) -> Dict[str, Any]:
    """Get show data from Spotify API using ID

    Args:
        sp (ExtendedSpotify): Spotify object
        show_id (str): Show ID

    Returns:
        Dict[str, Any]: Data on show
    """
    urn = f"spotify:shows:{show_id}"
    return sp.show(urn)


@login_if_missing(scope=None)
def get_show_id(sp: ExtendedSpotify, *, query: str) -> str:
    """Get ID of show that best matches the query (usually the name)

    Args:
        sp (ExtendedSpotify): Spotify object
        query (str): Search query

    Returns:
        str: Best matching show ID
    """
    res = sp.search(q=query, type="show", limit=1).get("shows").get("items")
    return res[0]["id"]


@login_if_missing(scope="user-read-playback-position")
def get_show_episodes(sp: ExtendedSpotify, *, show_id: str) -> List[EpisodeItem]:
    """Get list of episodes for a given show

    Args:
        sp (ExtendedSpotify): Spotify object
        show_id (str): Show ID

    Returns:
        List[EpisodeItem]: List of episode objects for the given show
    """
    yield from sp.show_episodes(show_id, limit=50, offset=0).get("items")
