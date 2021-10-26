from pathlib import Path
from spotify_flows.examples.collections import (
    combination_of_artists,
    lofi,
    saved_tracks,
    on_repeat,
    hits,
    balkan,
)
from spotify_flows.database import SpotifyDatabase


def main():
    database = SpotifyDatabase("data/spotify.db", op_table="operations")
    balkan().to_database(database)


if __name__ == "__main__":
    raise SystemExit(main())
