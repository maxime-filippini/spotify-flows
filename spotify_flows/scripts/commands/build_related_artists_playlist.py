from spotify_flows.spotify.collections import Artist


def build_related_artists_playlist(artist_id: str, out_playlist: str = None):
    if out_playlist is None:
        out_playlist = "My New Playlist"
    p = Artist.from_id(artist_id).related_artists(10, include=True).popular().random(5)
    p.to_playlist(playlist_name=out_playlist)
    return p


if __name__ == "__main__":
    build_related_artists_playlist("1C5jQlkf0TrFu6rmHZp2X5")
