from spotify_flows.spotify.collections import Artist
from spotify_flows.spotify.collections import ArtistCollection


def build_playlist_from_artists(artist_names, out_playlist: str = None):
    if out_playlist is None:
        out_playlist = "[" + ", ".join(artist_names) + "]"

    artists = [
        Artist.from_name(name).popular().first(10).shuffle() for name in artist_names
    ]
    p = ArtistCollection(id_="x", collections=artists).alternate()
    p.to_playlist(playlist_name=out_playlist)
    return p
