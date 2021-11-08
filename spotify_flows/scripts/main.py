import argparse

import spotify_flows.scripts.commands as commands


def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("--out_playlist", action="store")
    parser.add_argument("--smooth_energy", action="store_true")

    subparsers = parser.add_subparsers(dest="action")

    parser_pomodoro = subparsers.add_parser("pomodoro")
    parser_pomodoro.add_argument("in_playlist", action="store")

    parser_related = subparsers.add_parser("related")
    parser_related.add_argument("artist", action="store")

    parser_artists = subparsers.add_parser("artists")
    parser_artists.add_argument("artist_list", action="store", nargs="+")

    parser_artist_transition = subparsers.add_parser("artist_transition")
    parser_artist_transition.add_argument("from_", action="store")
    parser_artist_transition.add_argument("to_", action="store")

    parser_smoothen = subparsers.add_parser("smoothen")
    parser_smoothen.add_argument("in_playlist", action="store")
    parser_smoothen.add_argument("feature", action="store")

    parser_genres = subparsers.add_parser("genres")
    parser_genres.add_argument("--matches", action="store")
    parser_genres.add_argument("--contains", action="store")

    parser_genre_transition = subparsers.add_parser("genre_transition")
    parser_genre_transition.add_argument("from_", action="store")
    parser_genre_transition.add_argument("to_", action="store")

    # Parsing
    args, _common_args = parser.parse_known_args()
    common_args = parser.parse_args(_common_args)

    if args.action == "todays_podcasts":
        p = commands.todays_podcasts(args.out_playlist)

    elif args.action == "pomodoro":
        p = commands.build_pomodoro_from_playlist(
            in_playlist=args.in_playlist, out_playlist=common_args.out_playlist
        )

    if args.action == "related":
        p = commands.build_related_artists_playlist(
            artist_id=args.artist, out_playlist=common_args.out_playlist
        )

    if args.action == "artists":
        p = commands.build_playlist_from_artists(
            artist_names=args.artist_list, out_playlist=common_args.out_playlist
        )

    if args.action == "artist_transition":
        p = commands.build_artists_transition_playlist(
            start_artist_name=args.from_,
            end_artist_name=args.to_,
            out_playlist=common_args.out_playlist,
        )

    if args.action == "smoothen":
        p = commands.smoothen_playlist(
            playlist_name=args.in_playlist,
            feature=args.feature,
            out_playlist=common_args.out_playlist,
        )

    if args.action == "genre_transition":
        p = commands.build_genre_transition_playlist(
            from_=args.from_, to_=args.to_, out_playlist=common_args.out_playlist
        )

    if args.action == "genres":
        commands.list_genres(matches=args.matches, contains=args.contains)

    if args.smooth_energy:
        p.sort(by="audio_features.energy", ascending=True).to_playlist(
            common_args.out_playlist
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
