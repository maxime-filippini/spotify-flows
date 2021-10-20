from spotify_flows.spotify.collections import Artist
from spotify_flows.spotify.collections import Playlist
from spotify_flows.spotify.collections import Album
from spotify_flows.spotify.collections import Show


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
