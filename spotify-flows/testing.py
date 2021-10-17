from spotify.collections import Artist, Playlist, Album, Genre
from spotify.playlists import make_new_playlist


collection = Genre("hip-hop")


make_new_playlist(
    playlist_name="Hip hop recommended", tracks=[item.id for item in collection.items]
)
