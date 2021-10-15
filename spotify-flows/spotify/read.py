from typing import List

from spotify.login import login


def playlist_names():
    sp = login(scope="playlist-read-private")
    playlists = sp.current_user_playlists(limit=50)
    return playlists.get("items")


def top_tracks(ranges: List[str] = ["short_term", "medium_term", "long_term"]):
    sp = login(scope="user-top-read")

    return {
        range_: sp.current_user_top_tracks(time_range=range_, limit=50).get("items")
        for range_ in ranges
    }
