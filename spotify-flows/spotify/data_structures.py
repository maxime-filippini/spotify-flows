"""
    This module holds the elementary data structures used by the application
"""

# Standard library imports
from dataclasses import dataclass, fields, field
from typing import List, Dict, Any, Union
from datetime import datetime

# Third party imports

# Local imports

# Main body
class SpotifyDataStructure:
    @classmethod
    def trim_dict(cls, dict_):
        if dict_ is None:
            dict_ = {}

        class_fields = [field.name for field in fields(cls)]
        return {key: dict_[key] for key in class_fields if key in list(dict_.keys())}

    @classmethod
    def from_dict(cls, dict_):
        return cls(**cls.trim_dict(dict_))


@dataclass(eq=True, frozen=True)
class AudioFeaturesItem(SpotifyDataStructure):
    danceability: float = -1
    energy: float = -1
    key: float = -1
    loudness: float = 0
    mode: float = -1
    speechiness: float = -1
    acousticness: float = -1
    instrumentalness: float = -1
    liveness: float = -1
    valence: float = -1
    tempo: float = 0


@dataclass(eq=True, frozen=True)
class ArtistItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    popularity: int = 0


@dataclass(unsafe_hash=True)
class AlbumItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    release_date: str = ""
    artists: List[ArtistItem] = field(default_factory=list, compare=False)

    @classmethod
    def from_dict(cls, track_dict):
        if len(track_dict["release_date"]) == 19:
            track_dict["release_date"] = datetime.strptime(
                track_dict["release_date"], "%Y-%m-%d %H:%M:%S"
            )
        else:
            track_dict["release_date"] = datetime(int(track_dict["release_date"]), 1, 1)

        return super().from_dict(track_dict)


@dataclass(unsafe_hash=True)
class TrackItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    popularity: int = 0
    audio_features: AudioFeaturesItem = field(
        default=AudioFeaturesItem(), repr=False, compare=False
    )
    album: AlbumItem = AlbumItem()

    @classmethod
    def from_dict(cls, track_dict):

        album_dict = track_dict.get("album")

        artists = [
            ArtistItem.from_dict(artist_dict)
            for artist_dict in album_dict.get("artists")
        ]

        album_dict["artists"] = artists
        album = AlbumItem.from_dict(track_dict.get("album"))

        track_dict["album"] = album
        return super().from_dict(track_dict)


# @dataclass(eq=True, frozen=True)
# class PlaylistItem(SpotifyDataStructure):
#     id: str = ""
#     name: str = ""
#     type: str = ""
#     description: str = ""


# @dataclass(eq=True, frozen=True)
# class ShowItem(SpotifyDataStructure):
#     id: str = ""
#     name: str = ""


# @dataclass(eq=True, frozen=True)
# class EpisodeItem(SpotifyDataStructure):
#     id: str = ""
#     name: str = ""
#     runtime: str = ""
