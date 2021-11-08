import sqlite3
import pandas as pd
import networkx as nx
import pickle
from spotify_flows.database import SpotifyDatabase


def main():

    db = SpotifyDatabase("data/spotify.db", op_table="operations")
    df_genres = db.table_contents("genres")

    df_pairs = df_genres.drop(columns=["op_index"]).merge(df_genres, on="artist_id")
    df_pairs = df_pairs[df_pairs["genre_x"] != df_pairs["genre_y"]]

    df_pairs.loc[:, "letters"] = df_pairs["genre_x"] + df_pairs["genre_y"]
    df_pairs["letters"] = df_pairs["letters"].apply(lambda x: "".join(sorted(x)))

    df_letter_map = (
        df_pairs.groupby("letters").first().reset_index().drop(columns=["artist_id"])
    )

    # Count of common artists
    df_all_counts = (
        df_pairs[["letters", "artist_id"]]
        .groupby("letters")
        .count()
        .reset_index()
        .rename(columns={"artist_id": "common_count"})
    )
    df_all_counts = df_all_counts.groupby("letters").first().reset_index()
    df_all_counts = df_all_counts.merge(df_letter_map, on="letters")

    # Count of totals
    df_genre_counts = (
        df_genres.groupby("genre")
        .count()
        .reset_index()
        .rename(columns={"artist_id": "count"})
    )

    # Merge
    df_all_counts = (
        df_all_counts.merge(df_genre_counts, left_on="genre_x", right_on="genre")
        .drop(columns=["genre"])
        .rename(columns={"count": "count_x"})
        .merge(df_genre_counts, left_on="genre_y", right_on="genre")
        .drop(columns=["genre"])
        .rename(columns={"count": "count_y"})
    )

    # Compute total
    df_all_counts.loc[:, "total_count"] = (
        df_all_counts["count_x"] + df_all_counts["count_y"]
    )

    G = nx.Graph()

    for row in df_all_counts.iterrows():
        if row[1]["common_count"] > 0:
            genre_1 = row[1]["genre_x"]
            genre_2 = row[1]["genre_y"]
            weight = row[1]["total_count"] / row[1]["common_count"]

            G.add_edge(genre_1, genre_2, weight=weight)
            print(f"Added edge: {genre_1} to {genre_2} (weight={weight:.2f})")

    # Pickle the graph
    with open("data/genre_graph.p", "wb") as f:
        pickle.dump(G, f)


if __name__ == "__main__":
    raise SystemExit(main())
