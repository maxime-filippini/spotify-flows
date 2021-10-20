"""
    This module holds the API functions related to track information
"""

# Standard library imports
import copy
from typing import Any
from typing import Dict
from typing import List

# Third party imports

# Local imports
from .login import login_if_missing
from .classes import ExtendedSpotify
from .data_structures import TrackItem
from .data_structures import AudioFeaturesItem

# Main body
@login_if_missing(scope=None)
def read_track_from_id(sp: ExtendedSpotify, *, track_id: str) -> TrackItem:
    """Build a track item from a given ID

    Args:
        sp (ExtendedSpotify): Spotify object
        track_id (str): Track ID

    Returns:
        TrackItem: Track object
    """
    track_dict = sp.track(track_id)
    return TrackItem.from_dict(track_dict)


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
) -> Dict[str, AudioFeaturesItem]:
    """Retrieve audio features for a list of track IDs

    Args:
        sp (ExtendedSpotify): Spotify object
        track_ids (List[str]): Track IDs

    Returns:
        Dict[str, AudioFeaturesItem]: All audio features data
    """

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
        track_id: AudioFeaturesItem.from_dict(all_audio_features[i_track])
        for i_track, track_id in enumerate(track_ids)
    }
