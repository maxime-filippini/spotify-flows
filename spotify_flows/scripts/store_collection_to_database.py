from pathlib import Path
from spotify_flows.examples.collections import (
    combination_of_artists,
    lofi,
    saved_tracks,
    on_repeat,
)
from spotify_flows.database import create_spotify_database


def main():
    db_path = Path("spotify_flows/data/spotify.db")

    if not db_path.is_dir():
        create_spotify_database(db_path=db_path)
    on_repeat().to_database(db_path=db_path)


if __name__ == "__main__":
    raise SystemExit(main())
