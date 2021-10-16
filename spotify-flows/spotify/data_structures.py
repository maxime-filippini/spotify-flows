from dataclasses import dataclass, fields, field
from typing import List, Dict, Any, Union


TrackData = Union[Dict[str, Any], "TrackItem"]


class SpotifyDataStructure:
    @classmethod
    def from_dict(cls, d):
        if d is None:
            return cls()

        class_fields = [field.name for field in fields(cls)]
        new_dict = {key: d[key] for key in class_fields if key in list(d.keys())}
        return cls(**new_dict)


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
class TrackItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    popularity: int = 0
    release_date: str = ""
    audio_features: AudioFeaturesItem = field(default=AudioFeaturesItem(), repr=False)


@dataclass(eq=True, frozen=True)
class ArtistItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    popularity: int = 0


@dataclass(eq=True, frozen=True)
class AlbumItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    release_data: str = ""


@dataclass(eq=True, frozen=True)
class PlaylistItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    type: str = ""
    description: str = ""


@dataclass(eq=True, frozen=True)
class ShowItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""


@dataclass(eq=True, frozen=True)
class EpisodeItem(SpotifyDataStructure):
    id: str = ""
    name: str = ""
    runtime: str = ""
