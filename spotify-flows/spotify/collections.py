from typing import List
from typing import Any
from dataclasses import dataclass, field, asdict

import random
import copy

from spotify.playlists import get_playlist_id, get_playlist_tracks
from spotify.artists import get_artist_id, get_artist_popular_songs, get_artist_albums
from spotify.albums import get_album_id, get_album_songs, get_album_info
from spotify.tracks import get_audio_features
from spotify.data_structures import TrackItem

# TODO:
# FILTERS


@dataclass
class TrackCollection:
    id_: str = ""
    _items: List[Any] = field(default_factory=list)
    _audio_features_enriched: bool = False

    @property
    def items(self):
        return self._items

    @classmethod
    def from_id(cls, playlist_id: str):
        return cls(id_=playlist_id)

    @classmethod
    def from_name(cls, name: str):
        id_ = cls.func_get_id(name=name)
        return cls(id_=id_)

    def __str__(self):
        return "\n".join([str(item) for item in self.items])

    def __add__(self, other):
        new_items = list(set(self.items + other.items))
        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __sub__(self, other):
        new_items = list(set(self.items) - set(other.items))
        enriched = self._audio_features_enriched
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __truediv__(self, other):
        new_items = list(set(self.items).intersection(set(other.items)))
        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __mod__(self, other):
        self._items = [item for item in self.items if item not in other.items]
        new_items = [
            item
            for item_1, item_2 in zip(self.items, other.items)
            for item in (item_1, item_2)
        ]

        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def shuffle(self):
        new_items = copy.copy(self.items)
        random.shuffle(new_items)
        return TrackCollection(_items=new_items)

    def random(self, N: int):
        new_items = random.sample(self.items, n=max([N, len(self.items)]))
        return TrackCollection(_items=new_items)

    def remove_remixes(self):
        new_items = [item for item in self.items if "remix" not in item.name.lower()]
        return TrackCollection(_items=new_items)

    def sort(self, by: str, ascending: bool = True):
        str_attr = f"item.{by}"

        # Enrichment with audio features if needed
        if by.startswith("audio_features") and not self._audio_features_enriched:
            self._items = self._enrich_with_audio_features()
            self._audio_features_enriched = True

        sorted_items = sorted(
            self.items, key=eval(f"lambda item: {str_attr}"), reverse=(not ascending)
        )
        return TrackCollection(_items=sorted_items)

    def filter(self, criteria: str):
        str_filter = f"item.{criteria}"

        # Enrichment with audio features if needed
        if criteria.startswith("audio_features") and not self._audio_features_enriched:
            self._items = self._enrich_with_audio_features()
            self._audio_features_enriched = True

        filtered_items = [item for item in self.items if eval(str_filter)]
        return TrackCollection(_items=filtered_items)

    def _enrich_with_audio_features(self):
        audio_features_dict = get_audio_features(
            track_ids=[track.id for track in self.items]
        )

        return [
            TrackItem(
                **{**asdict(item), **{"audio_features": audio_features_dict[item.id]}}
            )
            for item in self.items
        ]


@dataclass
class Playlist(TrackCollection):
    func_get_id = lambda name: get_playlist_id(sp=None, playlist_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            return get_playlist_tracks(sp=None, playlist_id=self.id_)


class Album(TrackCollection):
    func_get_id = lambda name: get_album_id(sp=None, album_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            return get_album_songs(sp=None, album_id=self.id_)


class Artist(TrackCollection):
    func_get_id = lambda name: get_artist_id(sp=None, artist_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            return self.all_songs()

    def popular(self):
        items = get_artist_popular_songs(sp=None, artist_id=self.id_)
        return Artist(id_=self.id_, _items=items)

    def all_songs(self):
        album_data = get_artist_albums(artist_id=self.id_)
        album_collection = [Album.from_id(album.id) for album in album_data]
        all_tracks = [track for album in album_collection for track in album.items]

        # Remove duplicates
        idx = 0
        while idx < len(all_tracks):
            names = [track.name for track in all_tracks]

            if all_tracks[idx].name in names[:idx]:
                all_tracks.pop(idx)
            else:
                idx += 1

        return all_tracks
