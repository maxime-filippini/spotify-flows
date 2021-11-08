"""
    This module holds the API functions related to artist information
"""

# Standard library imports
from typing import List

# Third party imports

# Local imports
import spotify_flows.spotify.tracks as tracks
from .data_structures import TrackItem
from .data_structures import AlbumItem
from .data_structures import ArtistItem
from .login import login, login_if_missing
from .classes import ExtendedSpotify

# Main body
@login_if_missing(scope=None)
def get_artist_id(sp: ExtendedSpotify, *, artist_name: str) -> str:
    """Get ID of artist that matches the name provided

    Args:
        sp (ExtendedSpotify): Spotify object
        artist_name (str): Artist name

    Returns:
        str: Best matching artist ID
    """
    results = (
        sp.search(artist_name, type="artist", limit=10).get("artists").get("items")
    )
    sorted_results = sorted(results, key=lambda x: x["popularity"], reverse=True)
    return sorted_results[0].get("id")


@login_if_missing(scope=None)
def get_artist_popular_songs(sp: ExtendedSpotify, *, artist_id: str) -> List[TrackItem]:
    """Get the list of popular songs from a given artist

    Args:
        sp (ExtendedSpotify): Spotify object
        artist_id (str): Artist ID

    Returns:
        List[TrackItem]: Popular songs of the artist
    """
    tracks_data = sp.artist_top_tracks(artist_id=artist_id).get("tracks")
    track_ids = [track["id"] for track in tracks_data]

    for track_id in track_ids:
        yield tracks.read_track_from_id(track_id=track_id)


@login_if_missing(scope=None)
def get_artist_albums(
    sp: ExtendedSpotify, *, artist_id: str, album_type: str = "album"
) -> List[AlbumItem]:
    return sp.artist_albums(artist_id=artist_id, album_type=album_type).get("items")


@login_if_missing(scope=None)
def get_related_artists(sp: ExtendedSpotify, *, artist_id: str) -> List[ArtistItem]:
    return sp.artist_related_artists(artist_id=artist_id).get("artists")


@login_if_missing(scope=None)
def read_artists_from_id(sp: ExtendedSpotify, *, artist_ids: List[str]) -> ArtistItem:
    artist_data = []

    remaining_ids = artist_ids

    while remaining_ids:
        n = min(len(remaining_ids), 50)
        artist_data += sp.artists(artists=remaining_ids[:n]).get("artists")
        remaining_ids = remaining_ids[n:]

    return artist_data
