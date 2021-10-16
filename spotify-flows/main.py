from processes.processor import Playlist, Artist, Album
from spotify.playlists import get_playlist_tracks, make_new_playlist


def main():

    S = (Artist.from_name("voyage") / Artist.from_name("breskvica")) + (
        Artist.from_name("RAF Camora") / Artist.from_name("senidah")
    )

    print((Artist.from_name("RAF Camora")).items)

    # spb = (
    #     SpotifyProcessBuilder()
    #     + Artist.from_name("voyage")
    #     + Artist.from_name("breskvica")
    #     + Artist.from_name("jala brat")
    #     + Artist.from_name("senidah")
    # ).shuffle()

    # make_new_playlist(sp=None, playlist_name="Balkan_2", tracks=spb.items)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
