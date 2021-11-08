from spotify_flows.spotify.collections import Playlist
from spotify_flows.spotify.collections import Track
from spotify_flows.utils import init_logger


def build_pomodoro_from_playlist(in_playlist: str, out_playlist: str = None):
    if out_playlist is None:
        out_playlist = "My Pomodoro Playlist"

    playlist = Playlist.from_id(in_playlist).random(100)
    alarm_sound = Track.from_id("1hy7FfhaIcw4FjA9ZaE1Am")
    p = playlist.insert_at_time_intervals(alarm_sound, 30)
    p.to_playlist(playlist_name=out_playlist)

    return p


if __name__ == "__main__":
    init_logger()
    build_pomodoro_from_playlist("33ULcc1SJ2ipBgnpLgbv3M")
