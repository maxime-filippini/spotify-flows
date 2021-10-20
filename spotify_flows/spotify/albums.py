"""
    This module holds the API functions related to album information
"""

# Standard library imports
from typing import List
from typing import Dict
from typing import Any

# Third party imports

# Local imports
from .login import login_if_missing
from .classes import ExtendedSpotify
from .tracks import read_track_from_id
from .data_structures import TrackItem

# Main body
@login_if_missing(scope=None)
def get_album_id(sp: ExtendedSpotify, *, album_name: str) -> str:
    """Get ID of album that matches the name

    Args:
        sp (ExtendedSpotify): Spotify object
        album_name (str): Name of album

    Returns:
        str: ID of album
    """
    results = sp.search(album_name, type="album", limit=10).get("albums").get("items")
    return results[0].get("id")


@login_if_missing(scope=None)
def get_album_songs(sp: ExtendedSpotify, *, album_id: str) -> List[TrackItem]:
    """Get list of songs from a given album

    Args:
        sp (ExtendedSpotify): Spotify object
        album_id (str): Album ID

    Returns:
        List[TrackItem]: Track list
    """

    track_data = sp.album_tracks(album_id, limit=50, offset=0, market=None).get("items")
    track_ids = [track["id"] for track in track_data]
    return [read_track_from_id(sp=sp, track_id=track_id) for track_id in track_ids]


@login_if_missing(scope=None)
def get_album_info(sp: ExtendedSpotify, *, album_id: str) -> Dict[str, Any]:
    """Get album information from the Spotify API

    Args:
        sp (ExtendedSpotify): Spotify object
        album_id (str): Album ID

    Returns:
        Dict[str, Any]: Album information
    """
    return sp.albums([album_id])
