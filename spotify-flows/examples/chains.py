from spotify.collections import Artist, Playlist, Album
from spotify.playlists import make_new_playlist


# Example 1 - Popular songs from related Artists
collection = Artist.from_name("Dua Lipa").popular().filter(
    by="audio_features.danceability > 0.8"
).random(10) + Artist.from_name("Dua Lipa").related_artists().popular().filter(
    by="audio_features.danceability > 0.8"
).random(
    10
)


make_new_playlist(
    playlist_name="Dua Lipa & Related", tracks=[item.id for item in collection.items]
)
