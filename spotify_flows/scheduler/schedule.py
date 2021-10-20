from apscheduler.schedulers.background import BlockingScheduler
from spotify_flows.scripts.todays_podcasts import todays_podcasts
from spotify_flows.database.database import build_random_collection
from spotify_flows.spotify.collections import TrackCollection


scheduler = BlockingScheduler()


def random_playlist():
    items = build_random_collection(db_path="spotify_flows/data/spotify.db", N=20)
    TrackCollection(_items=items, id_="x").to_playlist(
        playlist_name="My random playlist"
    )


job = scheduler.add_job(todays_podcasts, "cron", hour=6)
job = scheduler.add_job(random_playlist, "cron", day_of_week="mon-fri", hour="8-18")
scheduler.start()
