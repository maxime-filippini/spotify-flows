from spotify.collections import Artist, Playlist, Album
from spotify.playlists import make_new_playlist


# # Example 1 - Popular songs from related Artists
# collection = (
#     Artist.from_name("Dua Lipa")
#     .filter(criteria="audio_features.danceability > 0.8")
#     .random(10)
#     + Artist.from_name("Dua Lipa")
#     .related_artists(n=10)
#     .popular()
#     .filter(criteria="audio_features.danceability > 0.5")
#     .random(10)
#     .shuffle()
# )


# make_new_playlist(
#     playlist_name="Dua Lipa & Related", tracks=[item.id for item in collection.items]
# )


# # Example 1 - Popular songs from related Artists
# collection = (
#     Artist.from_name("Andy C")
#     .related_artists(n=10)
#     .popular()
#     .filter(criteria="audio_features.energy > 0.8")
#     .sort(by="audio_features.energy", ascending=False)
# )


# make_new_playlist(
#     playlist_name="Andy C Energy!", tracks=[item.id for item in collection.items]
# )


# collection = (
#     Artist.from_name("Kwengface")
#     .related_artists(n=10)
#     .popular()
#     .sort(by="audio_features.energy", ascending=False)
# )


# make_new_playlist(playlist_name="Drill", tracks=[item.id for item in collection.items])


collection = Playlist.from_name("Drill") % Playlist.from_name("Andy C Energy!")


make_new_playlist(
    playlist_name="Drill & Dnb", tracks=[item.id for item in collection.items]
)
