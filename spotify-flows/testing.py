from requests.api import get
from spotify.collections import Artist, Playlist, Album, Genre
from spotify.playlists import make_new_playlist


# collection = Genre("hip-hop")


# make_new_playlist(
#     playlist_name="Hip hop recommended", tracks=[item.id for item in collection.items]
# )


from spotify.user import get_all_saved_tracks


tracks = get_all_saved_tracks()
