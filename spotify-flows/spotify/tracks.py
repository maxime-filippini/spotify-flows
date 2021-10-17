# Standard library imports
from typing import Dict
from typing import Any
from typing import List
import copy

# Third party imports

# Local imports
from spotify.classes import ExtendedSpotify
from spotify.data_structures import TrackItem, AudioFeaturesItem
from spotify.login import login_if_missing

# Main body
@login_if_missing(scope=None)
def read_track_from_id(sp: ExtendedSpotify, *, track_id: str) -> Dict[str, Any]:
    track_dict = sp.track(track_id)
    track_dict["release_date"] = track_dict["album"]["release_date"]
    return TrackItem.from_dict(track_dict)


@login_if_missing(scope=None)
def get_track_id(sp: ExtendedSpotify, *, track_name: str) -> str:
    results = sp.search(track_name, type="track", limit=10).get("tracks").get("items")
    sorted_results = sorted(results, key=lambda x: x["popularity"], reverse=True)
    return TrackItem.from_dict(sorted_results[0])


@login_if_missing(scope=None)
def get_audio_features(sp: ExtendedSpotify, *, track_ids: List[str]):
    max_len = 20
    offset = 0

    all_audio_features = []

    tracks_to_treat = copy.copy(track_ids)

    while tracks_to_treat:
        n = min(max_len, len(tracks_to_treat))

        all_audio_features = all_audio_features + sp.audio_features(
            tracks=tracks_to_treat[:n]
        )

        offset += n
        tracks_to_treat = tracks_to_treat[n:]

    return {
        track_id: AudioFeaturesItem.from_dict(all_audio_features[i_track])
        for i_track, track_id in enumerate(track_ids)
    }
