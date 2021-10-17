import sqlite3
from dataclasses import asdict
from typing import List
from datetime import datetime, timezone

import pandas as pd

from spotify.user import get_all_saved_tracks
from spotify.tracks import get_audio_features
from spotify.data_structures import TrackItem

CREATE_OPS_TABLE = """
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    op_type TEXT
)"""

CREATE_AUDIO_FEATURES_TABLE = """
CREATE TABLE IF NOT EXISTS audio_features (
 id TEXT PRIMARY KEY,
 danceability REAL,
 energy REAL,
 key REAL,
 loudness REAL,
 mode REAL,
 speechiness REAL,
 acousticness REAL,
 instrumentalness REAL,
 liveness REAL,
 valence REAL,
 tempo REAL,
 op_index INTEGER
)"""

CREATE_TRACKS_TABLE = """
CREATE TABLE IF NOT EXISTS tracks (
 id TEXT PRIMARY KEY,
 name TEXT,
 release_date TEXT,
 popularity INTEGER,
 op_index INTEGER
)"""

CREATE_COLLECTION_TABLE = """
CREATE TABLE IF NOT EXISTS tracks (
 id TEXT PRIMARY KEY,
 track_id TEXT,
)"""


def op_index(conn):
    c = conn.cursor()
    c.execute("SELECT MAX(id) from operations")
    max_id = c.fetchall()[0][0]

    if max_id is None:
        max_id = 0

    return max_id + 1


def record_operation(conn, op_type: str):
    c = conn.cursor()
    c.execute(
        f"INSERT INTO operations (date, op_type) VALUES ('{datetime.now(timezone.utc)}', '{op_type}')"
    )
    conn.commit()
    c.close()


def create_spotify_database(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(CREATE_OPS_TABLE)
        c.execute(CREATE_AUDIO_FEATURES_TABLE)
        c.execute(CREATE_TRACKS_TABLE)
        record_operation(conn, "db_creation")


def build_collection_from_id(id_: str, db_path: str):
    with sqlite3.connect(db_path) as conn:
        collection_query = f"SELECT track_id FROM collections WHERE id = '{id_}'"
        df_tracks = pd.read_sql(
            sql=f"SELECT * FROM tracks WHERE id in ({collection_query})", con=conn
        )

    if len(df_tracks) == 0:
        raise ValueError("Collection not found in database or empty")

    collection = [TrackItem.from_dict(track) for track in df_tracks.to_dict("records")]

    return collection


def store_tracks_in_database(collection, db_path: str) -> None:
    tracks = collection.items
    df_all_tracks = pd.DataFrame([asdict(track) for track in tracks])

    with sqlite3.connect(db_path) as conn:
        df_existing = pd.read_sql("SELECT * FROM tracks", con=conn)

        # Only keep new tracks
        df_merge = df_all_tracks.merge(
            right=df_existing["id"], how="left", on="id", indicator=True
        )

        df_tracks_to_add = (
            df_merge.drop(columns="audio_features")
            .loc[df_merge["_merge"] == "left_only"]
            .drop(columns="_merge")
            .drop_duplicates()
        )

        # Write audio features
        audio_features = get_audio_features(
            track_ids=list(df_tracks_to_add["id"].unique())
        )
        df_audio_features = (
            pd.DataFrame.from_dict(
                {key: asdict(value) for key, value in audio_features.items()},
                orient="index",
            )
            .reset_index()
            .rename(columns={"index": "id"})
        )

        # Perform the operations

        if len(df_audio_features) > 0:
            df_audio_features.loc[:, "op_index"] = op_index(conn)
            df_audio_features.to_sql(
                "audio_features", con=conn, if_exists="append", index=False
            )
            record_operation(conn, op_type="audio_features_addition")

        if len(df_tracks_to_add) > 0:
            df_tracks_to_add.loc[:, "op_index"] = op_index(conn)
            df_tracks_to_add.to_sql("tracks", con=conn, if_exists="append", index=False)
            record_operation(conn, op_type="tracks_addition")

        df_collection = df_all_tracks.loc[:, ["id"]].rename(columns={"id": "track_id"})
        df_collection.loc[:, "id"] = collection.id_
        df_collection.to_sql("collections", con=conn, if_exists="append", index=False)
        record_operation(conn, op_type="collection_addition")
