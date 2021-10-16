# Standard library imports
from typing import Dict
from typing import Any
from typing import Union
from pathlib import Path

# Third party imports
import yaml

# Local imports
from spotify.classes import ExtendedSpotify
from spotify.login import login_if_missing
from spotify.playlists import get_playlist_id, wipe_playlist

# Main body
@login_if_missing(scope="user-read-playback-position")
def read_show_from_id(sp: ExtendedSpotify, *, show_id: str) -> Dict[str, Any]:
    urn = f"spotify:shows:{show_id}"
    return sp.show(urn)


@login_if_missing(scope=None)
def search_podcasts(sp: ExtendedSpotify, *, query: str):
    res = sp.search(q=query, type="show", limit=50).get("shows").get("items")
    res = [{"name": r["name"], "n_ep": r["total_episodes"], "id": r["id"]} for r in res]
    sorted_res = sorted(res, key=lambda x: x["n_ep"], reverse=True)

    for r in sorted_res:
        print(r)


@login_if_missing(scope="playlist-modify-private playlist-read-private")
def store_newest_episodes_in_playlist(
    sp: ExtendedSpotify, *, playlist_name: str, file_path: Union[str, Path], date: str
):
    with open(file_path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        podcasts = data.get("list")

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
