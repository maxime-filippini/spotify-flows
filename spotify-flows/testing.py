from spotify.collections import (
    Artist,
    Playlist,
    Album,
    Genre,
    SavedTracks,
    TrackCollection,
)
from spotify.login import login
from pathlib import Path
from database.database import store_tracks_in_database, create_spotify_database


sp = login(scope=None)

# c = (
#     (
#         Artist.from_id("5LivRVTfsZa2k6FV0017fi")
#         + Artist.from_name("jala brat")
#         + Artist.from_name("voyage")
#         + Artist.from_name("senidah")
#     )
#     .filter("album.release_date.year > 2018")
#     .filter("audio_features.danceability > 0.7")
#     .random(20)
#     .set_id("Danceable Balkan")
# )


db_path = "data/spotify.db"
c = TrackCollection.from_db("saved_tracks", db_path=db_path)
# c = SavedTracks().set_id("saved_tracks")


# if not Path(db_path).is_dir():
#     create_spotify_database(db_path=db_path)

# store_tracks_in_database(collection=c, db_path=db_path)

print("")
