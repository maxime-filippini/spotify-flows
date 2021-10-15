from spotify.login import autologin, login
from spotify.read import top_tracks, playlist_names, read_show
from processes.common import store_newest_episodes_in_playlist


def search_podcasts():
    with login(scope=None) as sp:
        res = (
            sp.search(q="finance+news", type="show", limit=50).get("shows").get("items")
        )

        res = [
            {"name": r["name"], "n_ep": r["total_episodes"], "id": r["id"]} for r in res
        ]

        sorted_res = sorted(res, key=lambda x: x["n_ep"], reverse=True)
        for r in sorted_res:
            print(r)


def main():
    store_newest_episodes_in_playlist(
        "Today's podcasts", "data/podcast.yml", date="2021-10-14"
    )


if __name__ == "__main__":
    raise SystemExit(main())
