from spotify_flows.spotify.collections import Artist
from spotify_flows.spotify.collections import Playlist
from spotify_flows.spotify.collections import Album
from spotify_flows.spotify.collections import Show
from spotify_flows.spotify.collections import Track
from spotify_flows.spotify.collections import SavedTracks


def combination_of_artists():
    return (
        (
            Artist.from_name("dua lipa").remove_remixes()
            + Artist.from_name("rita ora").popular()
            + Artist.from_name("kanye west").popular()
        )
        .shuffle()
        .set_id("Example1.CombinationOfArtists")
    )


def pomodoro_lofi():
    playlist = Playlist.from_name(
        "lofi hip hop music - beats to relax/study to"
    ).random(100)
    alarm_sound = Track.from_id("1hy7FfhaIcw4FjA9ZaE1Am")

    return (
        playlist.trim_duration(30)
        + alarm_sound
        + playlist.trim_duration((30, 60))
        + alarm_sound
        + playlist.trim_duration((60, 90))
        + alarm_sound
        + playlist.trim_duration((90, 120))
        + alarm_sound
        + playlist.trim_duration((120, 150))
        + alarm_sound
    )


def lofi():
    return Playlist.from_name("lofi hip hop music - beats to relax/study to").set_id(
        "LoFi"
    )


def on_repeat():
    return Playlist.from_name("On Repeat").set_id("On repeat")


def saved_tracks():
    return SavedTracks().set_id("Saved tracks")


def random_from_playlist():
    playlist = Playlist.from_name(
        "lofi hip hop music - beats to relax/study to"
    ).random(1)
    return playlist
