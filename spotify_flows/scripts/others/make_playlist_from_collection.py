from spotify_flows.examples.collections import pomodoro_lofi


def main():
    pomodoro_lofi().to_playlist(playlist_name="Pomodoro LoFi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
