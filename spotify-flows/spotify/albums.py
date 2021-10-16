# Standard library imports
from typing import List
from dataclasses import dataclass

# Third party imports

# Local imports
from spotify.login import login_if_missing
from spotify.classes import ExtendedSpotify
from spotify.data_structures import ArtistItem
from spotify.data_structures import TrackItem

# Main body


@login_if_missing(scope=None)
def get_album_id(sp: ExtendedSpotify, *, album_name: str) -> str:
    results = sp.search(album_name, type="album", limit=10).get("albums").get("items")
    return results[0].get("id")


@login_if_missing(scope=None)
def get_album_songs(sp: ExtendedSpotify, *, album_id: str) -> List:
    track_data = sp.album_tracks(album_id, limit=50, offset=0, market=None).get("items")
    return [TrackItem.from_dict(track) for track in track_data]


@login_if_missing(scope=None)
def get_album_info(sp: ExtendedSpotify, *, album_id: str) -> List:
    return sp.albums([album_id])
