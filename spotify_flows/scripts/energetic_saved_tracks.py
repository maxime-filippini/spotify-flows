import pickle
import spotify_flows.spotify.collections as spocol


def main():
    # Load the artist graph
    with open("data/artist_graph.p", "rb") as f:
        graph = pickle.load(f)

    saved_tracks = spocol.SavedTracks().add_audio_features()
    energy_level = 0.2
    target_func = lambda x: x.audio_features.energy - energy_level
    saved_tracks.optimize(target_func, N=50).complex_sort(
        by="artist", graph=graph
    ).to_playlist(f"Energy~{energy_level}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
