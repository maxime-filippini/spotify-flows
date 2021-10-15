from typing import List

import spotipy

from spotify.login import autologin
from spotify.classes import ExtendedSpotify


def get_playlist_id(sp: ExtendedSpotify, *, playlist_name: str):
    playlists = {
        playlist["name"]: playlist["id"]
        for playlist in sp.current_user_playlists(limit=50).get("items")
    }
    return playlists[playlist_name]


def wipe_playlist(
    sp: ExtendedSpotify, *, playlist_id: str, types: List[str] = ["track", "episode"]
):
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
