from datetime import datetime, timedelta

import yaml

from spotify_flows.spotify.collections import TrackCollection, Show
from spotify_flows.spotify.playlists import make_new_playlist


def main():
    with open("spotify_flows/data/podcast.yml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader).get("list")

    collection = TrackCollection()

    start_time = datetime.today().replace(
        minute=0, hour=0, second=0, microsecond=0
    ) - timedelta(days=3)

    for item in data:
        collection = collection + Show.from_id(item["id"]).filter(
            lambda x: str(x.release_date) > str(start_time)
        )

    make_new_playlist(playlist_name="Today's podcasts", items=collection.items)


if __name__ == "__main__":
    raise SystemExit(main())
