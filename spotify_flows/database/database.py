"""
    This module holds the various database operations used by the application
"""

# Standard library imports
import yaml
import random
import sqlite3
import functools
from tqdm import tqdm
from typing import List
from contextlib import contextmanager
from datetime import datetime, timezone
from dataclasses import dataclass, field

# Third party imports
import pandas as pd

# Local imports
from spotify_flows.spotify.data_structures import TrackItem

# Main body
def connect_me(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.connect():
            rv = func(self, *args, **kwargs)
        return rv

    return wrapper


@dataclass
class Database:
    file_path: str
    conn: sqlite3.Connection = field(default=None, init=False)

    @contextmanager
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.file_path)
            yield
        finally:
            self.conn = None

    @connect_me
    def table_contents(self, tables: List[str]) -> pd.DataFrame:
        if isinstance(tables, str):
            return pd.read_sql(f"SELECT * FROM {tables}", self.conn)
        elif isinstance(tables, list):
            return [
                pd.read_sql(f"SELECT * FROM {table}", self.conn) for table in tables
            ]

    @connect_me
    def wipe_table(self, table: str) -> None:
        c = self.conn.cursor()
        c.execute(f"DELETE FROM {table}")
        self.conn.commit()

    @connect_me
    def delete_table(self, table: str) -> None:
        c = self.conn.cursor()
        c.execute(f"DROP TABLE {table}")
        self.conn.commit()

    @connect_me
    def create_database_file(self, schemas: List[str]) -> None:
        c = self.conn.cursor()
        for schema in schemas:
            c.execute(schema)

    @connect_me
    def run_query(self, query: str) -> None:
        c = self.conn.cursor()
        c.execute(query)
        self.conn.commit()

    @connect_me
    def write_dataframe(self, df: pd.DataFrame, table: str, **kwargs) -> None:
        df.to_sql(table, self.conn, **kwargs)


@dataclass
class SpotifyDatabase(Database):
    op_table: str

    @connect_me
    def _record_operation(self, op_type: str) -> None:
        c = self.conn.cursor()
        c.execute(
            f"INSERT INTO {self.op_table} (date, op_type) VALUES ('{datetime.now(timezone.utc)}', '{op_type}')"
        )
        self.conn.commit()
        c.close()

    @connect_me
    def _op_index(self) -> int:
        """Get operation index to be used

        Args:
            conn (sqlite3.Connection): Database connection

        Returns:
            int: Operation index
        """
        c = self.conn.cursor()
        c.execute("SELECT MAX(id) from operations")
        max_id = c.fetchall()[0][0]

        if max_id is None:
            max_id = 0

        return max_id + 1

    @connect_me
    def create_spotify_database(self, schema_file_path: str) -> None:
        with open(schema_file_path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        self.create_database_file(schemas=data.values())
        self._record_operation(self.conn, op_type="db_creation")

    def build_collection_from_track_ids(self, track_ids: List[str]) -> List[TrackItem]:

        (
            df_tracks,
            df_albums,
            df_albums_artists,
            df_artists,
            df_audio_features,
        ) = self.table_contents(
            ["tracks", "albums", "albums_artists", "artists", "audio_features"]
        )

        # Format the data
        track_data = df_tracks.loc[df_tracks["id"].isin(track_ids)].to_dict("records")

        collection = []
        for track_dict in track_data:
            # Get album data
            album_id = track_dict["album_id"]
            album_dict = df_albums.loc[df_albums["id"] == album_id].to_dict("records")[
                0
            ]

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

    @connect_me
    def build_collection_from_collection_id(self, id_: str) -> List[TrackItem]:
        df_collections = self.table_contents("collections")

        track_ids = df_collections.loc[df_collections["id"] == id_, "track_id"].tolist()
        return self.build_collection_from_track_ids(track_ids=track_ids)

    @connect_me
    def build_random_collection(self, N: int) -> List[TrackItem]:
        df_tracks = self.table_contents("tracks")
        track_ids = random.sample(list(df_tracks.loc[:, "id"].values), k=N)
        return self.build_collection_from_track_ids(track_ids=track_ids)

    @connect_me
    def store_tracks_in_database(self, collection) -> None:
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

        for table, df_data in table_map.items():
            self.enrich_database_table(df_data=df_data, table=table)

        df_collection = df_all_tracks.loc[:, ["id"]].rename(columns={"id": "track_id"})
        df_collection.loc[:, "id"] = collection.id_

        self.write_dataframe(
            df_collection, "collections", if_exists="append", index=False
        )
        self._record_operation(op_type="collection_addition")

    @connect_me
    def enrich_database_table(self, df_data: pd.DataFrame, table: str) -> None:

        df_existing = self.table_contents(table)

        # Parse dates (TODO: Integrate into table reading)
        for col in df_existing.columns:
            if "date" in col:
                df_existing.loc[:, col] = pd.to_datetime(
                    df_existing[col], format="%Y-%m-%d"
                )

        # Only keep new tracks
        if len(df_data) > 0:
            df_merge = df_data.merge(right=df_existing, how="left", indicator=True)

            df_to_add = (
                df_merge.loc[df_merge["_merge"] == "left_only"]
                .drop(columns="_merge")
                .loc[:, df_existing.columns]
                .drop_duplicates()
            )

            # Add to database
            df_to_add.loc[:, "op_index"] = self._op_index()

            if "id" in df_to_add.columns:
                valid_ids = ~df_to_add["id"].isin(df_existing["id"])
                self.write_dataframe(
                    df_to_add[valid_ids], table, if_exists="append", index=False
                )

            else:
                self.write_dataframe(df_to_add, table, if_exists="append", index=False)

            self._record_operation(op_type=f"record_addition_({table})")
