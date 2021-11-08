import pickle
import networkx as nx
import sqlite3
import pandas as pd
import numpy as np

from spotify_flows.spotify.collections import Artist, TrackCollection, Track


def build_genre_transition_playlist(from_: str, to_: str, out_playlist: str = None):

    # 1. Unpickle the graph
    with open("data/genre_graph.p", "rb") as f:
        genre_graph = pickle.load(f)

    # with open("data/artist_graph.p", "rb") as f:
    #     artist_graph = pickle.load(f)

    # 2. Determine shortest path
    path = nx.shortest_path(genre_graph, source=from_, target=to_, weight="weight")

    # 3. Build playlist
    with sqlite3.connect("data/spotify.db") as conn:
        df_genres = pd.read_sql("SELECT * FROM genres", con=conn)
        df_artists = pd.read_sql("SELECT * FROM artists", con=conn)

    playlist_tracks = []
    playlist_track_ids = []
    latest_track = None

    for genre in path:
        artist_id = (
            df_genres.loc[df_genres["genre"] == genre]
            .merge(df_artists, left_on="artist_id", right_on="id")
            .sort_values("popularity", ascending=False)
            .loc[:, "artist_id"]
            .iloc[0]
        )

        popular_tracks = Artist.from_id(artist_id).popular().add_audio_features()

        if latest_track is None:
            latest_track = next(popular_tracks.items)
            energy_level = latest_track.audio_features.energy

        else:
            all_tracks = list(popular_tracks.items)

            all_valid_tracks = [
                track for track in all_tracks if track.id not in playlist_track_ids
            ]

            all_energy_levels = np.array(
                [track.audio_features.energy for track in all_valid_tracks]
            )
            energy_diffs = np.abs(all_energy_levels - energy_level)
            i_latest_track = np.where(energy_diffs == energy_diffs.min())[0][0]
            latest_track = all_tracks[i_latest_track]

        if latest_track.id not in playlist_track_ids:
            playlist_tracks.append(latest_track)
            playlist_track_ids.append(latest_track.id)

    if out_playlist is None:
        out_playlist = f"{from_} -> {to_}"

    TrackCollection(id_=out_playlist, _items=playlist_tracks).to_playlist()


if __name__ == "__main__":
    build_genre_transition_playlist(
        from_="new rave", to_="suomi rock", out_playlist="Test"
    )
