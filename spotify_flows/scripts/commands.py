import argparse
from typing import Optional
from typing import Sequence

from .todays_podcasts import todays_podcasts


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("--todays_podcasts", action="store_true")
    parser

    args = parser.parse_args(argv)

    if args.todays_podcasts:
        todays_podcasts()


if __name__ == "__main__":
    raise SystemExit(main())
