import pickle
import networkx as nx
import sqlite3
import random
from networkx.algorithms.coloring.greedy_coloring import strategy_random_sequential
import pandas as pd
import numpy as np
import copy

from spotify_flows.spotify.collections import Artist, CollectionCollection
from spotify_flows.spotify.artists import read_artists_from_id, get_artist_popular_songs
from spotify_flows.analysis.graphs import artist_popularity_weight_func


def main(start_artist_id: str, end_artist_id: str):

    # 1. Unpickle the graph
    with open("data/genre_graph.p", "rb") as f:
        genre_graph = pickle.load(f)

    with open("data/artist_graph.p", "rb") as f:
        artist_graph = pickle.load(f)

    start_artist = read_artists_from_id(artist_ids=[start_artist_id])[0]
    end_artist = read_artists_from_id(artist_ids=[end_artist_id])[0]

    path = nx.dijkstra_path(
        artist_graph,
        source=start_artist_id,
        target=end_artist_id,
        weight=lambda u, v, d: artist_popularity_weight_func(
            artist_graph, start_artist, u, v, d
        ),
    )

    start = Artist.from_id(path[0]).popular().add_audio_features().random(1)
    target_audio = copy.copy(list(start.items)[0].audio_features)

    target_func = lambda x: (x.audio_features.energy - target_audio.energy) + (
        x.audio_features.danceability - target_audio.danceability
    )

    CollectionCollection(
        id_="collection",
        collections=[start]
        + [
            Artist.from_id(artist_id)
            .popular()
            .add_audio_features()
            .optimize(target_func)
            for artist_id in path
        ],
    ).to_playlist(f"{start_artist.name} -> {end_artist.name}")


if __name__ == "__main__":
    raise SystemExit(
        main(
            start_artist_id="4ufkY8hmhmYl4aCnzv3dLE",
            end_artist_id="5POPLEqoZcENY4ZNXQWZHB",
        )
    )
