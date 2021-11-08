from spotify_flows.spotify.collections import Playlist


def smoothen_playlist(playlist_name: str, feature: str, out_playlist: str = None):
    if out_playlist is None:
        out_playlist = playlist_name

    p = Playlist.from_name(playlist_name)
    sort_criteria = f"audio_features.{feature}"
    p.sort(by=sort_criteria, ascending=True).to_playlist(out_playlist)
    return p


if __name__ == "__main__":
    smoothen_playlist("Monika's special", feature="energy", out_playlist="Test")
