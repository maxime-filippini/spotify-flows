"""
    This module holds the API functions related to artist information
"""

# Standard library imports

# Third party imports

# Local imports
from spotify.data_structures import ArtistItem, TrackItem, AlbumItem
from spotify.login import login_if_missing
from spotify.tracks import read_track_from_id
from spotify.classes import ExtendedSpotify

# Main body
@login_if_missing(scope=None)
def get_artist_id(sp: ExtendedSpotify, *, artist_name: str) -> str:
    results = (
        sp.search(artist_name, type="artist", limit=10).get("artists").get("items")
    )
    sorted_results = sorted(results, key=lambda x: x["popularity"], reverse=True)
    return sorted_results[0].get("id")


@login_if_missing(scope=None)
def get_artist_popular_songs(sp: ExtendedSpotify, *, artist_id: str):
    tracks_data = sp.artist_top_tracks(artist_id=artist_id).get("tracks")
    track_ids = [track["id"] for track in tracks_data]
    return [read_track_from_id(track_id=track_id) for track_id in track_ids]


@login_if_missing(scope=None)
def get_artist_albums(
    sp: ExtendedSpotify, *, artist_id: str, album_type: str = "album"
):
    albums = sp.artist_albums(artist_id=artist_id, album_type=album_type).get("items")
    return [AlbumItem.from_dict(album) for album in albums]


@login_if_missing(scope=None)
def get_related_artists(sp: ExtendedSpotify, *, artist_id: str):
    artists_dict = sp.artist_related_artists(artist_id=artist_id).get("artists")
    return [ArtistItem.from_dict(artist) for artist in artists_dict]
