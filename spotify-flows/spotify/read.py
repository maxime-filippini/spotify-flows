from typing import List

import spotipy

from spotify.login import autologin


@autologin(scope="playlist-read-private")
def playlist_names(sp: spotipy.Spotify):
    playlists = sp.current_user_playlists(limit=50)
    return playlists.get("items")


@autologin(scope="user-top-read")
def top_tracks(
    sp: spotipy.Spotify,
    *,
    ranges: List[str] = ["short_term", "medium_term", "long_term"],
):
    return {
        range_: sp.current_user_top_tracks(time_range=range_, limit=50).get("items")
        for range_ in ranges
    }


@autologin(scope="user-read-playback-position")
def read_show(sp: spotipy.Spotify, *, show_id: str):
    urn = f"spotify:shows:{show_id}"
    return sp.show(urn)


@autologin(scope="user-read-playback-position")
def read_track(sp: spotipy.Spotify, *, track_id: str):
    urn = f"spotify:tracks:{track_id}"
    return sp.track(urn)
