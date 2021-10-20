from spotify_flows.examples.collections import combination_of_artists
from spotify_flows.spotify.playlists import make_new_playlist
from spotify_flows.spotify.user import playlist_names


def main():
    combination_of_artists().to_playlist(playlist_name="Example Playlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
