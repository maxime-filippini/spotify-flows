from spotify_flows.database.database import (
    create_spotify_database,
    store_tracks_in_database,
)
from spotify_flows.spotify.user import get_all_saved_tracks
from spotify_flows.spotify.collections import TrackCollection, Playlist, Artist

from pathlib import Path

# collection = (
#     (
#         Artist.from_name("dua lipa").popular()
#         + Artist.from_name("machine gun kelly").popular()
#     )
#     .shuffle()
#     .set_id("Dua Lipa + MGK")
# )

collection = (
    TrackCollection.from_db(id_="Dua Lipa + MGK", db_path=Path("data/spotify.db"))
    + Artist.from_name("rihanna").popular()
)

print("")
# if __name__ == "__main__":
#     db_path = Path("data/spotify.db")

#     if not db_path.is_dir():
#         create_spotify_database(db_path=db_path)

#     store_tracks_in_database(collection=collection, db_path=db_path)
