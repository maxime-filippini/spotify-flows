from spotify.read import top_tracks, playlist_names


def main():
    res = top_tracks()
    # for r in res:
    #     print(r["name"])
    print(res)


if __name__ == "__main__":
    raise SystemExit(main())
