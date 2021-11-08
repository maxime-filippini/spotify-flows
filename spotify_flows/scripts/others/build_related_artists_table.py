import sqlite3
import pandas as pd
from tqdm import tqdm
import copy

from spotify_flows.analysis.graphs import graph_recursion
from spotify_flows.database import SpotifyDatabase


def main():
    db = SpotifyDatabase("data/spotify.db", op_table="operations")
    df_related, df_artists = db.table_contents(["related", "artists"])

    # Artists to load
    all_artist_ids = (
        df_artists.loc[~df_artists["id"].isin(df_related["artist_id"]), "id"]
        .unique()
        .tolist()
    )

    # Load memo
    if len(df_related) > 0:
        memo = (
            df_related.groupby("artist_id")
            .apply(lambda x: x["related_artist_id"].unique().tolist())
            .to_dict()
        )
    else:
        memo = {}

    # Build inks
    for artist_id in tqdm(all_artist_ids):
        if artist_id not in memo:
            old_memo = copy.deepcopy(memo)
            graph_recursion(artist_id, memo)

            # Write to database
            memo_to_write = {k: v for k, v in memo.items() if k not in old_memo}

            if memo_to_write:
                print(f"Writing {len(memo_to_write)} rows to database")
                df_to_write = pd.DataFrame(
                    [
                        {"artist_id": key, "related_artist_id": v}
                        for key, value in memo_to_write.items()
                        for v in value
                    ]
                )

                db.write_dataframe(
                    df_to_write, "related", index=False, if_exists="append"
                )


if __name__ == "__main__":
    raise SystemExit(main())
