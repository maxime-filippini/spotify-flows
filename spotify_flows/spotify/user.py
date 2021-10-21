"""
    This module holds the API functions related to track information
"""

# Standard library imports
from typing import Any
from typing import List
from typing import Dict

# Third party imports

# Local imports
from .login import login_if_missing
from .classes import ExtendedSpotify
from .data_structures import TrackItem

# Main body
@login_if_missing(scope="playlist-read-private")
def playlist_names(sp: ExtendedSpotify) -> List[str]:
    """Retrieve all playlist names for the user

    Args:
        sp (ExtendedSpotify): Spotify object

    Returns:
        List[str]: Playlist names
    """
    playlists = sp.current_user_playlists(limit=50).get("items")
    return [playlist["item"] for playlist in playlists]


@login_if_missing(scope="user-top-read")
def get_user_top_tracks(
    sp: ExtendedSpotify,
    *,
    ranges: List[str] = ["short_term", "medium_term", "long_term"],
) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieve the user's top track

    Args:
        sp (ExtendedSpotify): Spotify object
        ranges (List[str], optional): List of ranges to retrieve. Defaults to ["short_term", "medium_term", "long_term"].

    Returns:
        Dict[str, List[Dict[str, Any]]]: Saved tracks per range
    """

    out = {}
    for range_ in ranges:
        tracks_data = sp.current_user_top_tracks(time_range=range_, limit=50).get(
            "items"
        )
        out[range_] = [TrackItem.from_dict(track) for track in tracks_data]

    return out


@login_if_missing(scope="user-read-playback-position")
def get_recommendations_for_genre(
    sp: ExtendedSpotify, *, genre_names: List[str]
) -> List[TrackItem]:
    """Retrieve Spotify recommendation for a given list of genres

    Args:
        sp (ExtendedSpotify): Spotify object
        genre_names (List[str]): List of genres

    Returns:
        List[TrackItem]: Recommended tracks
    """
    tracks = sp.recommendations(seed_genres=genre_names).get("tracks")

    for track in tracks:
        yield TrackItem.from_dict(track)


@login_if_missing(scope="user-library-read")
def get_all_saved_tracks(sp: ExtendedSpotify) -> List[TrackItem]:
    """Retrieve all of the user's saved tracks

    Args:
        sp (ExtendedSpotify): Spotify object

    Returns:
        List[TrackItem]: Saved tracks
    """

    all_results = sp.current_user_saved_tracks(limit=50)
    next = all_results.get("next")

    while next:
        raw_results = sp.next(raw_results)
        next = raw_results.get("next")
        new_results = raw_results
        all_results = all_results + new_results

    for result in all_results:
        yield TrackItem.from_dict(
            {
                **result.get("track"),
                "release_date": result["track"]["album"]["release_date"],
            }
        )
