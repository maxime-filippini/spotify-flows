import pickle
import networkx as nx
import pandas as pd
import numpy as np
import copy

from spotify_flows.spotify.collections import Artist, CollectionCollection
from spotify_flows.spotify.data_structures import ArtistItem
from spotify_flows.spotify.artists import read_artists_from_id, get_artist_id
from spotify_flows.analysis.graphs import artist_popularity_weight_func


def build_artists_transition_playlist(
    start_artist_name: str, end_artist_name: str, out_playlist: str = None
):

    # 1. Unpickle the graph
    with open("data/genre_graph.p", "rb") as f:
        genre_graph = pickle.load(f)

    with open("data/artist_graph.p", "rb") as f:
        artist_graph = pickle.load(f)

    # Read artists
    start_artist_id = get_artist_id(artist_name=start_artist_name)
    end_artist_id = get_artist_id(artist_name=end_artist_name)

    start_artist = ArtistItem.from_dict(
        read_artists_from_id(artist_ids=[start_artist_id])[0]
    )
    end_artist = ArtistItem.from_dict(
        read_artists_from_id(artist_ids=[end_artist_id])[0]
    )

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

    if out_playlist is None:
        out_playlist = f"{start_artist.name} -> {end_artist.name}"

    p = CollectionCollection(
        id_="collection",
        collections=[start]
        + [
            Artist.from_id(artist_id)
            .popular()
            .add_audio_features()
            .optimize(target_func, N=1)
            for artist_id in path
        ],
    )

    p.to_playlist(out_playlist)

    return p


if __name__ == "__main__":
    build_artists_transition_playlist("dua lipa", "senidah")
