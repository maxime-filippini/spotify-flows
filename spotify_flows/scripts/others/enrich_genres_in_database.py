import sqlite3
import pandas as pd
from spotify_flows.spotify.artists import read_artists_from_id
from spotify_flows.database import SpotifyDatabase


def main():
    db = SpotifyDatabase("data/spotify.db", op_table="operations")
    df_genres, df_artists = db.table_contents(["genres", "artists"])

    enriched_artist_ids = df_genres.loc[:, "artist_id"].tolist()
    all_artist_ids = df_artists.loc[:, "id"].tolist()

    artists_to_enrich = [id for id in all_artist_ids if id not in enriched_artist_ids]
    remaining_artists = artists_to_enrich

    while remaining_artists:
        n = min(len(remaining_artists), 50)
        artists = read_artists_from_id(artist_ids=remaining_artists[:n])
        df_data = pd.DataFrame(
            [
                {"artist_id": artist.id, "genre": genre}
                for artist in artists
                for genre in artist.genres
            ]
        )

        db.enrich_database_table(df_data=df_data, table="genres")
        remaining_artists = remaining_artists[n:]


if __name__ == "__main__":
    raise SystemExit(main())
