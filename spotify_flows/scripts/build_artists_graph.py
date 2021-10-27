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
    df_related, df_genres, df_artists = db.table_contents(
        ["related", "genres", "artists"]
    )

    G = nx.Graph()

    # Build dataframe to build the nodes
    # artist_id, related_id, genres, popularity
    df_packed_genres = (
        df_genres.groupby("artist_id")
        .apply(lambda df: df["genre"].unique().tolist())
        .reset_index()
        .rename(columns={0: "genre"})
    )

    df_nodes = df_artists.merge(
        df_packed_genres, left_on="id", right_on="artist_id"
    ).loc[:, ["id", "genre", "popularity"]]

    node_data = [(d.pop("id"), d) for d in df_nodes.to_dict("records")]

    G.add_nodes_from(node_data)

    # Build dataframe to build the edges
    # artist_id, relative_artist_id, pop_diff
    df_edges = (
        df_related.merge(
            df_artists[["id", "popularity"]],
            left_on="artist_id",
            right_on="id",
            how="inner",
        )
        .merge(
            df_artists[["id", "popularity"]],
            left_on="related_artist_id",
            right_on="id",
            how="inner",
        )
        .loc[:, ["artist_id", "related_artist_id", "popularity_x", "popularity_y"]]
    )

    df_edges.loc[:, "pop_diff"] = (
        df_edges["popularity_x"] - df_edges["popularity_y"]
    ).abs()
    df_edges.drop(columns=["popularity_x", "popularity_y"], inplace=True)

    edge_data = [
        (d.pop("artist_id"), d.pop("related_artist_id"), d)
        for d in df_edges.to_dict("records")
    ]

    G.add_edges_from(edge_data)

    with open("data/artist_graph.p", "wb") as f:
        pickle.dump(G, f)


if __name__ == "__main__":
    raise SystemExit(main())
