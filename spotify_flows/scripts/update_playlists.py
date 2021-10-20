import sqlite3

import pandas as pd

from spotify_flows.spotify.collections import TrackCollection
from spotify_flows.database.database import get_collection_ids, store_tracks_in_database


def main():
    db_path = "data/spotify.db"

    with sqlite3.connect(db_path) as conn:
        df_collections = pd.read_sql("SELECT id FROM collections", con=conn)

    for collection_id in df_collections["id"].unique():
        collection = TrackCollection.from_db(collection_id, db_path=db_path)
        store_tracks_in_database(collection=collection, db_path=db_path)


if __name__ == "__main__":
    raise SystemExit(main())
