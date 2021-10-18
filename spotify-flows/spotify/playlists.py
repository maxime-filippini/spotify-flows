"""
    This module holds the API functions related to playlist information
"""

# Standard library imports
from typing import List

# Third party imports
import copy

# Local imports
from spotify.login import login_if_missing
from spotify.classes import ExtendedSpotify
from spotify.data_structures import TrackItem
from spotify.tracks import read_track_from_id

# Main body
@login_if_missing(scope="playlist-read-private playlist-modify-private")
def get_playlist_id(sp: ExtendedSpotify, *, playlist_name: str) -> str:

    playlists = {
        playlist["name"]: playlist["id"]
        for playlist in sp.current_user_playlists(limit=50).get("items")
    }

    return playlists[playlist_name]


@login_if_missing(scope="playlist-modify-private playlist-modify-public")
def make_new_playlist(sp: ExtendedSpotify, *, playlist_name: str, tracks: List[str]):
    try:
        playlist_id = get_playlist_id(sp, playlist_name=playlist_name)
    except KeyError as e:
        sp.user_playlist_create(user=sp.me()["id"], name=playlist_name)
        playlist_id = get_playlist_id(sp=sp, playlist_name=playlist_name)

    wipe_playlist(sp=sp, playlist_id=playlist_id, types=["track"])

    offset = 0
    remaining_tracks = copy.copy(tracks)

    while remaining_tracks:
        n = min(len(remaining_tracks), 20)
        sp.playlist_add_items(
            playlist_id=playlist_id, items=remaining_tracks[:n], position=offset
        )
        remaining_tracks = remaining_tracks[n:]
        offset += n


@login_if_missing(scope="playlist-read-private")
def get_playlist_tracks(sp: ExtendedSpotify, *, playlist_id: str) -> str:
    all_track_ids = []
    loaded_track_ids = []
    offset = 0
    limit = 50

    def load_track_ids(offset):
        tracks = sp.playlist_items(
            playlist_id,
            offset=offset,
            limit=limit,
            fields="items.track",
            additional_types=["track"],
        ).get("items")
        return [item["track"]["id"] for item in tracks]

    while True:
        loaded_track_ids = load_track_ids(offset)
        offset += len(loaded_track_ids)
        all_track_ids = all_track_ids + loaded_track_ids

        if len(loaded_track_ids) < limit:
            break

    return [read_track_from_id(sp=sp, track_id=track_id) for track_id in all_track_ids]


@login_if_missing(scope="playlist-modify-private")
def wipe_playlist(
    sp: ExtendedSpotify, *, playlist_id: str, types: List[str] = ["track", "episode"]
) -> None:
    for type_ in types:
        all_tracks = sp.playlist_items(
            playlist_id, offset=0, fields="items.track.id", additional_types=[type_]
        ).get("items")

        track_ids = [i["track"]["id"] for i in all_tracks]

        if type_ == "track":
            sp.playlist_remove_all_occurrences_of_items(
                playlist_id, list(set(track_ids))
            )

        elif type_ == "episode":
            sp.playlist_remove_episodes(playlist_id, list(set(track_ids)))


@login_if_missing(scope="playlist-modify-private playlist-read-private")
def edit_playlist_details(
    sp: ExtendedSpotify, *, playlist_name: str, name: str = None, desc: str = None
):
    playlist_id = get_playlist_id(sp, playlist_name=playlist_name)

    new_details = {}
    if name:
        new_details["name"] = name
    if desc:
        new_details["description"] = desc

    sp.playlist_change_details(playlist_id, **new_details)


def build_playlist_from_collection():
    pass
