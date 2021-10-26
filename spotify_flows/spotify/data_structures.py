"""
    This module holds the elementary data structures used by the application
"""

# Standard library imports
from typing import Any
from typing import List
from typing import Dict
from dataclasses import dataclass, fields, field

# Third party imports

# Local imports
from spotify_flows.utils.dates import date_parsing

# Main body
class SpotifyDataStructure:
    """Base class for Spotify data structures"""

    @classmethod
    def trim_dict(cls, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """Trim input dictionary based on dataclass fields

        Args:
            dict_ (Dict[str, Any]): Dictionary holding construction data

        Returns:
            Dict[str, Any]: Dictionary with ommitted keys
        """
        if dict_ is None:
            dict_ = {}

        class_fields = [field.name for field in fields(cls)]
        return {key: dict_[key] for key in class_fields if key in list(dict_.keys())}

    @classmethod
    def from_dict(cls, dict_: Dict[str, Any]) -> "SpotifyDataStructure":
        """Construct data structure from input dictionary

        Args:
            dict_ (Dict[str, Any]): Dictionary holding construction data

        Returns:
            SpotifyDataStructure: Data structure object
        """
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
    genres: List[str] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class AlbumItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    release_date: str = ""
    artists: List[ArtistItem] = field(default_factory=list, compare=False)

    @classmethod
    def from_dict(cls, track_dict):
        release_date_str = track_dict["release_date"]
        track_dict["release_date"] = date_parsing(release_date_str)
        return super().from_dict(track_dict)


@dataclass(unsafe_hash=True)
class TrackItem(SpotifyDataStructure):
    item_type = "track"

    id: str = ""
    name: str = ""
    popularity: int = 0
    duration_ms: int = 0
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


@dataclass(eq=True, frozen=True)
class EpisodeItem(SpotifyDataStructure):
    item_type = "episode"

    id: str = ""
    name: str = ""
    duration_ms: str = ""
    release_date: str = ""
    description: str = field(default="", repr=False)

    @classmethod
    def from_dict(cls, ep_dict):
        release_date_str = ep_dict["release_date"]
        ep_dict["release_date"] = date_parsing(release_date_str)
        return super().from_dict(ep_dict)
