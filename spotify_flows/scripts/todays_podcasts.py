# Standard library imports
from datetime import datetime, timedelta

# Third party imports
import yaml

# Local imports
from spotify_flows.spotify.collections import Show
from spotify_flows.spotify.playlists import make_new_playlist, edit_playlist_details

# Main body
def todays_podcasts():

    # 1. Load data
    with open("data/podcast.yml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader).get("list")

    # 2. Determine the date criteria
    start_time = datetime.today().replace(
        minute=0, hour=0, second=0, microsecond=0
    ) - timedelta(days=1)

    filter_ = lambda x: str(x.release_date) >= str(start_time)

    # Build up the collection of shows
    collection = sum(
        [Show.from_id(item["id"]).filter(criteria_func=filter_) for item in data]
    ).sort(by="duration_ms", ascending=True)

    # Add to playlist
    playlist_id = make_new_playlist(
        playlist_name="Today's podcasts", items=collection.items
    )

    # Update playlist
    edit_playlist_details(
        playlist_id=playlist_id,
        desc=f"Loaded on {datetime.today().strftime('%Y-%m-%d')}",
    )


if __name__ == "__main__":
    raise SystemExit(todays_podcasts())
