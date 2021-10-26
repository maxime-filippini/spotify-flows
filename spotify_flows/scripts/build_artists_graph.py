# Standard library imports
import sqlite3
import pickle

# Third party imports
import pandas as pd
import networkx as nx
from tqdm import tqdm

# Local imports
from spotify_flows.database import SpotifyDatabase

# Main body


def main():
    db = SpotifyDatabase("data/spotify.db", op_table="operations")
    df, df_genres, df_artists = db.table_contents(["related", "genres", "artists"])

    G = nx.Graph()
    artists = list(df["artist_id"].unique())

    for artist in tqdm(artists):
        rel = df.loc[df["artist_id"] == artist, "related_artist_id"].unique()
        genres = (
            df_genres.loc[df_genres["artist_id"] == artist, "genre"].unique().tolist()
        )

        artist_popularity = df_artists.loc[
            df_artists["id"] == artist, "popularity"
        ].values[0]

        G.add_node(artist, genres=genres, popularity=artist_popularity)

        for r in rel:
            rel_popularity = df_artists.loc[df_artists["id"] == r, "popularity"].values[
                0
            ]

            G.add_edge(artist, r, pop_diff=abs(artist_popularity - rel_popularity))

    with open("data/artist_graph.p", "wb") as f:
        pickle.dump(G, f)


if __name__ == "__main__":
    raise SystemExit(main())
