import datetime
from typing import Union
from pathlib import Path

import spotipy
import yaml

from spotify.login import login
from spotify.playlists import get_playlist_id, wipe_playlist


def store_newest_episodes_in_playlist(
    playlist_name: str, file_path: Union[str, Path], date: str
):
    with open(file_path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    podcasts = data.get("list")

    with login(scope="playlist-modify-private playlist-read-private") as sp:

        playlist_id = get_playlist_id(sp, playlist_name=playlist_name)
        wipe_playlist(sp, playlist_id=playlist_id, types=["episode"])

        # Add episodes
        eps = [
            item["id"]
            for podcast in podcasts
            for item in sp.show_episodes(podcast["id"], limit=10, offset=0).get("items")
            if item["release_date"] == date
        ]

        sp.playlist_add_episodes(playlist_id=playlist_id, items=eps, position=0)
