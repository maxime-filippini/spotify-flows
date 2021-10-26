# Standard library imports
import sqlite3
from dataclasses import asdict

# Third party imports
import pandas as pd

from spotify_flows.spotify.artists import read_artists_from_id
from spotify_flows.database import SpotifyDatabase

# Main body


def main():
    db = SpotifyDatabase("data/spotify.db", op_table="operations")
    df_related, df_artists = db.table_contents(["related", "artists"])

    df_related = df_related.drop_duplicates()
    enriched_artist_ids = df_artists.loc[:, "id"].unique().tolist()

    all_artist_ids = set(
        df_related["artist_id"].tolist() + df_related["related_artist_id"].tolist()
    )
    artists_to_enrich = [id for id in all_artist_ids if id not in enriched_artist_ids]
    remaining_artists = artists_to_enrich

    while remaining_artists:
        n = min(len(remaining_artists), 50)
        artists = read_artists_from_id(artist_ids=remaining_artists[:n])
        df_data = pd.DataFrame([asdict(artist) for artist in artists]).drop(
            columns=["genres"]
        )

        db.enrich_database_table(df_data=df_data, table="artists")
        remaining_artists = remaining_artists[n:]


if __name__ == "__main__":
    raise SystemExit(main())
