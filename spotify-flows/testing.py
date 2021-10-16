from spotify.login import login
from spotify.collections import Artist, Album, Playlist

sp = login(scope="playlist-read-private")


# A = Artist.from_name("dua lipa").remove_remixes()
# A = Album.from_name("certified lover boy")
P = Playlist.from_name("Motivation Mix").filter(
    criteria="audio_features.instrumentalness >= 0.7"
)

print([p.popularity for p in P.items])
print(P)
print(len(P.items))
