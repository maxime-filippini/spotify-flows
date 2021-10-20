"""
    This module holds the various database operations used by the application
"""

# Standard library imports
import sqlite3
from dataclasses import asdict
from typing import List
from datetime import datetime, timezone

# Third party imports
import pandas as pd

# Local imports
from spotify_flows.spotify.tracks import get_audio_features
from spotify_flows.spotify.data_structures import TrackItem

# Schemas

CREATE_AUDIO_FEATURES_TABLE = """
CREATE TABLE IF NOT EXISTS audio_features (
 track_id TEXT PRIMARY KEY,
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

CREATE_OPS_TABLE = "CREATE TABLE IF NOT EXISTS operations (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, op_type TEXT)"
CREATE_TRACKS_TABLE = "CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, name TEXT, popularity INTEGER, album_id TEXT, op_index INTEGER)"
CREATE_ARTISTS_TABLE = "CREATE TABLE IF NOT EXISTS artists (id TEXT PRIMARY KEY, name TEXT, popularity INTEGER, op_index INTEGER)"
CREATE_ALBUMS_TABLE = "CREATE TABLE IF NOT EXISTS albums (id TEXT PRIMARY KEY, name TEXT, release_date DATE, op_index INTEGER)"
CREATE_ALBUM_ARTIST_TABLE = "CREATE TABLE IF NOT EXISTS albums_artists (artist_id TEXT, album_id TEXT, op_index INTEGER)"
CREATE_COLLECTION_TABLE = (
    "CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, track_id TEXT)"
)

table_schemas = [
    CREATE_OPS_TABLE,
    CREATE_AUDIO_FEATURES_TABLE,
    CREATE_TRACKS_TABLE,
    CREATE_ALBUMS_TABLE,
    CREATE_ARTISTS_TABLE,
    CREATE_ALBUM_ARTIST_TABLE,
    CREATE_COLLECTION_TABLE,
]


def op_index(conn: sqlite3.Connection) -> int:
    """Get operation index to be used

    Args:
        conn (sqlite3.Connection): Database connection

    Returns:
        int: Operation index
    """
    c = conn.cursor()
    c.execute("SELECT MAX(id) from operations")
    max_id = c.fetchall()[0][0]

    if max_id is None:
        max_id = 0

    return max_id + 1


def record_operation(conn: sqlite3.Connection, op_type: str) -> None:
    """Record an operation into the operations table of the database

    Args:
        conn (sqlite3.Connection): Database connection
        op_type (str): Type of operation
    """

    c = conn.cursor()
    c.execute(
        f"INSERT INTO operations (date, op_type) VALUES ('{datetime.now(timezone.utc)}', '{op_type}')"
    )
    conn.commit()
    c.close()


def create_spotify_database(db_path: str) -> None:
    """Create the database file and its tables

    Args:
        db_path (str): Path to database file
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for table_schema in table_schemas:
            c.execute(table_schema)
        record_operation(conn, "db_creation")


def build_collection_from_id(id_: str, db_path: str) -> List[TrackItem]:
    """Build a list of track items from a given collection ID

    Args:
        id_ (str): Collection identifier
        db_path (str): Path to database

    Raises:
        ValueError: Collection does not exist or has no tracks

    Returns:
        List[TrackItem]: Output
    """

    with sqlite3.connect(db_path) as conn:
        df_collections = pd.read_sql(f"SELECT * FROM collections", con=conn)
        df_tracks = pd.read_sql(f"SELECT * FROM tracks", con=conn)
        df_albums = pd.read_sql(f"SELECT * FROM albums", con=conn)
        df_albums_artists = pd.read_sql(f"SELECT * FROM albums_artists", con=conn)
        df_artists = pd.read_sql(f"SELECT * FROM artists", con=conn)
        df_audio_features = pd.read_sql(f"SELECT * FROM audio_features", con=conn)

    # Early exit
    if len(df_tracks) == 0:
        raise ValueError("Collection not found in database or empty")

    # Format the data
    track_ids = df_collections.loc[df_collections["id"] == id_, "track_id"].tolist()
    track_data = df_tracks.loc[df_tracks["id"].isin(track_ids)].to_dict("records")

    collection = []
    for track_dict in track_data:
        # Get album data
        album_id = track_dict["album_id"]
        album_dict = df_albums.loc[df_albums["id"] == album_id].to_dict("records")[0]

        # Get artists ids
        artist_ids = df_albums_artists.loc[
            df_albums_artists["album_id"] == album_id, "artist_id"
        ].tolist()
        artist_dict = df_artists.loc[df_artists["id"].isin(artist_ids)].to_dict(
            "records"
        )

        # Add artist data to album
        album_dict["artists"] = artist_dict

        # Add audio features
        audio_features_dict = df_audio_features[
            df_audio_features["track_id"] == track_dict["id"]
        ].to_dict("records")[0]

        # Add to track
        track_dict["album"] = album_dict
        track_dict["audio_features"] = audio_features_dict

        collection.append(TrackItem.from_dict(track_dict))

    return collection


def store_tracks_in_database(collection, db_path: str) -> None:
    """Collection object to database

    Args:
        collection (TrackCollection): Collection to store
        db_path (str): Path to database
    """

    (
        df_all_tracks,
        df_all_artists,
        df_all_albums,
        df_audio_features,
        df_album_artist,
    ) = collection.to_dataframes()

    table_map = {
        "tracks": df_all_tracks,
        "artists": df_all_artists,
        "albums": df_all_albums,
        "audio_features": df_audio_features,
        "albums_artists": df_album_artist,
    }

    with sqlite3.connect(db_path) as conn:

        for table, df_data in table_map.items():
            df_existing = pd.read_sql(f"SELECT * FROM {table}", con=conn)
            for col in df_existing.columns:
                if "date" in col:
                    df_existing.loc[:, col] = pd.to_datetime(
                        df_existing[col], format="%Y-%m-%d"
                    )

            # Only keep new tracks
            df_merge = df_data.merge(right=df_existing, how="left", indicator=True)

            df_to_add = (
                df_merge.loc[df_merge["_merge"] == "left_only"]
                .drop(columns="_merge")
                .drop_duplicates()
            )

            # Add to database
            if len(df_to_add) > 0:
                df_to_add.loc[:, "op_index"] = op_index(conn)
                df_to_add.to_sql(table, con=conn, if_exists="append", index=False)
                record_operation(conn, op_type=f"record_addition_({table})")

        df_collection = df_all_tracks.loc[:, ["id"]].rename(columns={"id": "track_id"})
        df_collection.loc[:, "id"] = collection.id_
        df_collection.to_sql("collections", con=conn, if_exists="append", index=False)
        record_operation(conn, op_type="collection_addition")
