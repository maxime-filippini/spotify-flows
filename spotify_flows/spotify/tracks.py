"""
    This module holds the API functions related to track information
"""

# Standard library imports
import copy
from typing import Dict
from typing import List
from typing import Any
from dataclasses import asdict

# Third party imports

# Local imports
from .albums import get_album_info
from .login import login_if_missing
from .classes import ExtendedSpotify
from .artists import read_artists_from_id

# Main body
@login_if_missing(scope=None)
def read_track_from_id(sp: ExtendedSpotify, *, track_id: str) -> Dict[str, Any]:
    track_dict = sp.track(track_id)
    album_dict = get_album_info(sp=sp, album_id=track_dict["album"]["id"])
    artist_data = read_artists_from_id(
        sp=sp, artist_ids=[artist["id"] for artist in album_dict["artists"]]
    )

    album_dict["artists"] = artist_data
    track_dict["album"] = album_dict

    return track_dict


@login_if_missing(scope=None)
def get_track_id(sp: ExtendedSpotify, *, track_name: str) -> str:
    """Get ID of track that best matches track name

    Args:
        sp (ExtendedSpotify): Spotify object
        track_name (str): Track name

    Returns:
        str: Best matching ID
    """
    results = sp.search(track_name, type="track", limit=10).get("tracks").get("items")
    sorted_results = sorted(results, key=lambda x: x["popularity"], reverse=True)
    return sorted_results[0]["id"]


@login_if_missing(scope=None)
def get_audio_features(
    sp: ExtendedSpotify, *, track_ids: List[str]
) -> Dict[str, Dict[str, Any]]:
    max_len = 20
    offset = 0
    all_audio_features = []
    tracks_to_treat = copy.copy(track_ids)

    while tracks_to_treat:
        n = min(max_len, len(tracks_to_treat))
        all_audio_features = all_audio_features + sp.audio_features(
            tracks=tracks_to_treat[:n]
        )
        offset += n
        tracks_to_treat = tracks_to_treat[n:]

    return {
        track_id: all_audio_features[i_track]
        for i_track, track_id in enumerate(track_ids)
    }
