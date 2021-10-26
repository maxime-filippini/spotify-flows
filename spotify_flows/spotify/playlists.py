"""
    This module holds the API functions related to playlist information
"""

# Standard library imports
from typing import List
from typing import Union

# Third party imports
import copy

# Local imports
from .login import login_if_missing
from .classes import ExtendedSpotify
from .tracks import read_track_from_id
from .data_structures import TrackItem
from .data_structures import EpisodeItem

# Main body
@login_if_missing(scope="playlist-read-private playlist-modify-private")
def get_playlist_id(sp: ExtendedSpotify, *, playlist_name: str) -> str:
    """Get ID of playlist matching the given name

    Args:
        sp (ExtendedSpotify): Spotify object
        playlist_name (str): Playlist name

    Returns:
        str: Playlist ID
    """
    playlists = {
        playlist["name"]: playlist["id"]
        for playlist in sp.current_user_playlists(limit=50).get("items")
    }

    return playlists[playlist_name]


def import_items_to_playlist(
    sp: ExtendedSpotify, items: List[Union[TrackItem, EpisodeItem]], playlist_id: str
) -> None:
    """Add items to a given playlist

    Args:
        sp (ExtendedSpotify): Spotify object
        items (List[Union[TrackItem, EpisodeItem]]): List of tracks or episodes (or mixed)
        playlist_id (str): Playlist ID
    """

    for i_item, item in enumerate(items):
        sp.playlist_add_items(
            playlist_id=playlist_id,
            items=[item.id],
            position=i_item,
            item_type=item.item_type,
        )


@login_if_missing(scope="playlist-modify-private")
def make_new_playlist(
    sp: ExtendedSpotify,
    *,
    playlist_name: str,
    items: List[Union[TrackItem, EpisodeItem]],
) -> str:
    """Make playlist and add items

    Args:
        sp (ExtendedSpotify): Spotify object
        playlist_name (str): Name of playlist to be created
        items (List[Union[TrackItem, EpisodeItem]]): Items to be added to the playlist
    """

    try:
        playlist_id = get_playlist_id(sp, playlist_name=playlist_name)
    except KeyError as e:
        sp.user_playlist_create(user=sp.me()["id"], name=playlist_name)
        playlist_id = get_playlist_id(sp=sp, playlist_name=playlist_name)

    wipe_playlist(sp=sp, playlist_id=playlist_id)
    import_items_to_playlist(sp=sp, items=list(items), playlist_id=playlist_id)
    return playlist_id


@login_if_missing(scope="playlist-read-private")
def get_playlist_tracks(sp: ExtendedSpotify, *, playlist_id: str) -> List[TrackItem]:
    """Retrieve list of tracks in a given playlist

    Args:
        sp (ExtendedSpotify): Spotify object
        playlist_id (str): Playlist ID

    Returns:
        List[TrackItem]: List of tracks within playlist
    """

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

    for track_id in all_track_ids:
        yield read_track_from_id(sp=sp, track_id=track_id)


@login_if_missing(scope="playlist-modify-private")
def wipe_playlist(sp: ExtendedSpotify, *, playlist_id: str) -> None:
    """Delete all items within the given playlist

    Args:
        sp (ExtendedSpotify): Spotify object
        playlist_id (str): Playlist ID
    """

    all_items = sp.playlist_items(
        playlist_id, offset=0, fields="items.track.id, items.track.type"
    ).get("items")

    tracks = [item for item in all_items if item["track"]["type"] == "track"]
    episodes = [item for item in all_items if item["track"]["type"] == "episode"]

    if tracks:
        track_ids = [track["track"]["id"] for track in tracks]
        sp.playlist_remove_all_occurrences_of_items(playlist_id, list(set(track_ids)))

    if episodes:
        episode_ids = [episode["track"]["id"] for episode in episodes]
        sp.playlist_remove_episodes(playlist_id, list(set(episode_ids)))


@login_if_missing(scope="playlist-modify-private playlist-modify-public")
def edit_playlist_details(
    sp: ExtendedSpotify, *, playlist_id: str, name: str = None, desc: str = None
) -> None:
    """Edit details of a given playlist

    Args:
        sp (ExtendedSpotify): Spotify object
        playlist_id (str): Playlist ID
        name (str, optional): Updated playlist name. Defaults to None.
        desc (str, optional): Updated playlist description. Defaults to None.
    """

    new_details = {}
    if name:
        new_details["name"] = name
    if desc:
        new_details["description"] = desc

    if new_details:
        sp.playlist_change_details(playlist_id, **new_details)
