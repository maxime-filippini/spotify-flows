"""
    This module holds the API functions related to track information
"""

# Standard library imports
from typing import List
from typing import Dict
from typing import Any

# Third party imports
import spotipy
from spotipy.client import Spotify

# Local imports
from spotify.login import login_if_missing
from spotify.classes import ExtendedSpotify
from spotify.data_structures import TrackItem

# Main body
@login_if_missing(scope="playlist-read-private")
def playlist_names(sp: ExtendedSpotify) -> Dict[str, Any]:
    playlists = sp.current_user_playlists(limit=50)
    return playlists.get("items")


@login_if_missing(scope="user-top-read")
def get_user_top_tracks(
    sp: ExtendedSpotify,
    *,
    ranges: List[str] = ["short_term", "medium_term", "long_term"],
) -> Dict[str, List[Dict[str, Any]]]:
    out = {}
    for range_ in ranges:
        tracks_data = sp.current_user_top_tracks(time_range=range_, limit=50).get(
            "items"
        )
        out[range_] = [TrackItem.from_dict(track) for track in tracks_data]

    return out


@login_if_missing(scope="user-read-playback-position")
def read_show_from_id(sp: ExtendedSpotify, *, show_id: str) -> Dict[str, Any]:
    urn = f"spotify:shows:{show_id}"
    return sp.show(urn)


@login_if_missing(scope="user-read-playback-position")
def get_recommendations_for_genre(
    sp: ExtendedSpotify, *, genre_names: List[str]
) -> Dict[str, Any]:
    tracks = sp.recommendations(seed_genres=genre_names).get("tracks")
    return [TrackItem.from_dict(track) for track in tracks]


@login_if_missing(scope="user-library-read")
def get_all_saved_tracks(sp: ExtendedSpotify):
    raw_results = sp.current_user_saved_tracks(limit=50)

    def format_results(results: Dict[str, Any]):
        return [
            TrackItem.from_dict(
                {
                    **result.get("track"),
                    "release_date": result["track"]["album"]["release_date"],
                }
            )
            for result in raw_results.get("items")
        ]

    all_results = format_results(raw_results)
    next = raw_results.get("next")

    while next:
        raw_results = sp.next(raw_results)
        next = raw_results.get("next")
        new_results = format_results(raw_results)
        all_results = all_results + new_results

    return all_results
