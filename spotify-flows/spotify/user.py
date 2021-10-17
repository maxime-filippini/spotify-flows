# Standard library imports
from typing import List
from typing import Dict
from typing import Any

# Third party imports
import spotipy

# Local imports
from spotify.login import login_if_missing
from spotify.data_structures import TrackItem

# Main body
@login_if_missing(scope="playlist-read-private")
def playlist_names(sp: spotipy.Spotify) -> Dict[str, Any]:
    playlists = sp.current_user_playlists(limit=50)
    return playlists.get("items")


@login_if_missing(scope="user-top-read")
def user_top_tracks(
    sp: spotipy.Spotify,
    *,
    ranges: List[str] = ["short_term", "medium_term", "long_term"],
) -> Dict[str, List[Dict[str, Any]]]:
    return {
        range_: sp.current_user_top_tracks(time_range=range_, limit=50).get("items")
        for range_ in ranges
    }


@login_if_missing(scope="user-read-playback-position")
def read_show_from_id(sp: spotipy.Spotify, *, show_id: str) -> Dict[str, Any]:
    urn = f"spotify:shows:{show_id}"
    return sp.show(urn)


@login_if_missing(scope="user-read-playback-position")
def read_track_from_id(sp: spotipy.Spotify, *, track_id: str) -> Dict[str, Any]:
    urn = f"spotify:tracks:{track_id}"
    return sp.track(urn)


@login_if_missing(scope="user-read-playback-position")
def get_recommendations_for_genre(
    sp: spotipy.Spotify, *, genre_names: List[str]
) -> Dict[str, Any]:
    tracks = sp.recommendations(seed_genres=genre_names).get("tracks")
    return [TrackItem.from_dict(track) for track in tracks]
