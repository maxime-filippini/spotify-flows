from .spotify.collections import (
    Artist,
    Playlist,
    Album,
    Genre,
    SavedTracks,
    TrackCollection,
    Show,
)
from .spotify.login import login
from pathlib import Path
from .database.database import store_tracks_in_database, create_spotify_database
from .spotify.playlists import make_new_playlist


sp = login(scope=None)

c = (
    Artist.from_name("Wilkinson")
    .related_artists(n=10, include=True)
    .filter(lambda x: x.audio_features.instrumentalness < 0.1)
    .sort(by="audio_features.instrumentalness", ascending=True)
    .set_id("Vocal D&B")
)


# db_path = "data/spotify.db"
# c = TrackCollection.from_db("saved_tracks", db_path=db_path)
# c = SavedTracks().set_id("saved_tracks")


# if not Path(db_path).is_dir():
#     create_spotify_database(db_path=db_path)

# store_tracks_in_database(collection=c, db_path=db_path)


# c = Show.from_name("Freakonomics").sort(by="release_date", ascending=False).first(
#     10
# ) % Show.from_name("Today, Explained").sort(by="release_date", ascending=False).first(
#     10
# )

make_new_playlist(playlist_name="Vocal D&B", items=c.items)


print(c)

print("")
