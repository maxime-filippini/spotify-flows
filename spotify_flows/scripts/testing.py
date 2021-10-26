import pickle
import networkx as nx
from networkx.algorithms.coloring.greedy_coloring import strategy_random_sequential
import pandas as pd
import numpy as np
import spotify_flows.spotify.collections as spocol
from spotify_flows.spotify.artists import read_artists_from_id


def main():
    with open("data/artist_graph.p", "rb") as f:
        artist_graph = pickle.load(f)

    path = nx.shortest_path(
        artist_graph, source="2Qtzo4vZyl2YPd22eC6zJR", target="57n1OF36WvtOeATY6WQ6iw"
    )

    target_energy = 0.7
    target_func = lambda x: x.audio_features.energy - target_energy

    col = spocol.CollectionCollection(
        collections=[
            spocol.Artist.from_id(artist_id)
            .popular()
            .add_audio_features()
            .optimize(target_func)
            for artist_id in path
        ]
    )

    for track in col.items:
        print(track)


if __name__ == "__main__":
    main()
