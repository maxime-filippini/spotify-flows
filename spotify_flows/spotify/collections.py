"""
    This module is the main API used to create track collections
"""

# Standard library imports
import copy
import random
import inspect
from typing import Any
from typing import List
from typing import Tuple
from typing import Callable
from dataclasses import dataclass, field, asdict

# Third party imports
import pandas as pd

# Local imports
from .login import login
from .data_structures import TrackItem
from .tracks import get_audio_features

from .albums import get_album_id
from .albums import get_album_songs
from .podcasts import get_show_id
from .podcasts import get_show_episodes
from .user import get_all_saved_tracks
from .user import get_recommendations_for_genre
from spotify_flows.database.database import store_tracks_in_database
from spotify_flows.database.database import build_collection_from_id

from .artists import get_artist_id
from .artists import get_artist_albums
from .artists import get_related_artists
from .artists import get_artist_popular_songs

from .playlists import get_playlist_id
from .playlists import make_new_playlist
from .playlists import get_playlist_tracks


# Main body
@dataclass
class TrackCollection:
    """Class representing a collection of tracks. Can be chained together through a
    variety of defined methods."""

    read_items_from_db = lambda id_, db_path: build_collection_from_id(
        id_=id_, db_path=db_path
    )

    sp = login(
        scope="playlist-modify-private playlist-modify-public user-read-playback-position user-library-read"
    )

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
    def from_db(cls, id_: str, db_path: str):
        items = cls.read_items_from_db(id_=id_, db_path=db_path)
        return TrackCollection(id_=id_, _items=items)

    @classmethod
    def from_name(cls, name: str):
        id_ = cls.func_get_id(name=name)
        return cls(id_=id_)

    def __str__(self) -> str:
        return "\n".join([str(item) for item in self.items])

    def __add__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the addition of two collections. Items get concatenated.

        Returns:
            TrackCollection: Collection object with combined items
        """
        new_items = list(set(self.items + other.items))
        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __radd__(self, other: "TrackCollection") -> "TrackCollection":
        """Used when building track collections from list of other track collections

        Returns:
            TrackCollection: Sum of two collections
        """
        if other == 0:
            return self
        else:
            return self + other

    def __sub__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the substraction of two collections. Items from other get removed from items from self.

        Returns:
            TrackCollection: Collection object with modified items.
        """
        new_items = list(set(self.items) - set(other.items))
        enriched = self._audio_features_enriched
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __truediv__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the division of two collections.

        Returns:
            TrackCollection: Items are intersection of self and other
        """
        new_items = list(set(self.items).intersection(set(other.items)))
        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def __mod__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the modulo of two collections

        Returns:
            TrackCollection: Items are alternates of self and other.
        """
        current_items = self.items
        other_items = other.items
        current_items = [item for item in current_items if item not in other_items]

        new_items = [
            item
            for item_1, item_2 in zip(current_items, other_items)
            for item in (item_1, item_2)
        ]

        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items, _audio_features_enriched=enriched)

    def to_dataframes(self) -> Tuple[pd.DataFrame]:
        """Transforms items into dataframes, used for storage in database.

        Returns:
            Tuple[pd.DataFrame]: Representation of items as dataframes
        """

        # Enrich with audio features
        self._items = self._enrich_with_audio_features(self.items)
        tracks = copy.copy(self.items)

        # Extract data
        album_artist = [
            {"album_id": track.album.id, "artist_id": artist.id}
            for track in tracks
            for artist in track.album.artists
        ]

        all_tracks = [asdict(track) for track in tracks]

        all_audio_features = [
            {"track_id": track["id"], **track["audio_features"]} for track in all_tracks
        ]

        all_albums = [asdict(track.album) for track in tracks]
        all_artists = [artist for album in all_albums for artist in album["artists"]]

        # Build dataframes
        df_all_artists = pd.DataFrame(all_artists)
        df_all_albums = pd.DataFrame(all_albums).drop(columns="artists")
        df_audio_features = pd.DataFrame(all_audio_features)

        df_all_tracks = pd.DataFrame(all_tracks)
        df_all_tracks.loc[:, "album_id"] = df_all_tracks["album"].apply(
            lambda x: x["id"]
        )

        df_all_tracks.drop(columns=["album", "audio_features"], inplace=True)
        df_album_artist = pd.DataFrame(album_artist)

        return (
            df_all_tracks,
            df_all_artists,
            df_all_albums,
            df_audio_features,
            df_album_artist,
        )

    def shuffle(self) -> "TrackCollection":
        """Shuffle items

        Returns:
            TrackCollection: Object with items shuffled.
        """
        new_items = copy.copy(self.items)
        random.shuffle(new_items)
        self._items = new_items
        return self

    def random(self, N: int) -> "TrackCollection":
        """Sample items randomly

        Args:
            N (int): Number of items to pick

        Returns:
            TrackCollection: Object with new items
        """
        new_items = random.sample(self.items, min([N, len(self.items)]))
        self._items = new_items
        return self

    def remove_remixes(self) -> "TrackCollection":
        """Remove remixes from items

        Returns:
            TrackCollection: Object with new items
        """
        banned_words = ["remix", "mixed"]

        new_items = [
            item
            for item in self.items
            if all(
                [(banned_word not in item.name.lower()) for banned_word in banned_words]
            )
        ]
        self._items = new_items
        return self

    def sort(self, by: str, ascending: bool = True) -> "TrackCollection":
        """Sort items

        Args:
            by (str): Criteria used for sorting
            ascending (bool, optional): Ascending order. Defaults to True.

        Returns:
            TrackCollection: Object with sorted items
        """
        str_attr = f"item.{by}"

        # Enrichment with audio features if needed
        if by.startswith("audio_features") and not self._audio_features_enriched:
            self._items = self._enrich_with_audio_features(items=self.items)
            self._audio_features_enriched = True

        sorted_items = sorted(
            self.items, key=eval(f"lambda item: {str_attr}"), reverse=(not ascending)
        )
        return TrackCollection(
            _items=sorted_items, _audio_features_enriched=self._audio_features_enriched
        )

    def filter(self, criteria_func: Callable[..., Any]) -> "TrackCollection":
        """Filter items by certain criteria function

        Args:
            criteria_func (Callable[..., Any]): Criteria used for filtering

        Returns:
            TrackCollection: Object with filtered items
        """

        # Enrichment with audio features if needed
        if (
            "audio_features" in inspect.getsource(criteria_func)
            and not self._audio_features_enriched
        ):
            self._items = self._enrich_with_audio_features(items=self.items)
            self._audio_features_enriched = True

        filtered_items = [item for item in self.items if criteria_func(item)]
        return TrackCollection(
            _items=filtered_items,
            _audio_features_enriched=self._audio_features_enriched,
        )

    def _enrich_with_audio_features(self, items: List[TrackItem]) -> List[TrackItem]:
        """Get items enriched with audio features

        Args:
            items (List[TrackItem]): Items to enrich

        Returns:
            List[TrackItem]: Enriched items
        """
        audio_features_dict = get_audio_features(
            track_ids=[track.id for track in items]
        )

        for item in items:
            item.audio_features = audio_features_dict[item.id]

        return items

    def set_id(self, id_: str) -> "TrackCollection":
        """Add ID to collection, e.g. to use for storage in a database

        Returns:
            TrackCollection: Same collection, but with ID
        """
        return TrackCollection(
            id_=id_,
            _items=self.items,
            _audio_features_enriched=self._audio_features_enriched,
        )

    def remove_duplicates(self: "TrackCollection") -> "TrackCollection":
        """Remove duplicate tracks from items based on ID

        Returns:
            TrackCollection: Collection with no duplicate tracks
        """

        # By ID
        items = copy.copy(self.items)

        idx = 0
        while idx < len(items):
            names = [item.name for item in items]

            if items[idx].name in names[:idx]:
                items.pop(idx)
            else:
                idx += 1

        self._items = items
        return self

    def first(self, n: int) -> "TrackCollection":
        """First n items

        Returns:
            TrackCollection: Collection with trimmed items
        """

        items = self.items
        k = min((n, len(items)))
        self._items = items[:k]
        return self

    def to_playlist(self, playlist_name: str) -> None:
        if playlist_name is None:
            playlist_name = self.id_

        make_new_playlist(sp=self.sp, playlist_name=playlist_name, items=self.items)

    def to_database(self, db_path: str) -> None:
        store_tracks_in_database(collection=self, db_path=db_path)


@dataclass
class Playlist(TrackCollection):
    """Class representing a Playlist's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_playlist_id(sp=cls.sp, playlist_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            if self.id_:
                return get_playlist_tracks(sp=self.sp, playlist_id=self.id_)
            else:
                return []


class Album(TrackCollection):
    """Class representing an Album's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_album_id(sp=cls.sp, album_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            if self.id_:
                return get_album_songs(sp=self.sp, album_id=self.id_)
            else:
                return []


class Artist(TrackCollection):
    """Class representing an Artist's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_artist_id(sp=cls.sp, artist_name=name)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            if self.id_:
                return self.all_songs()
            else:
                return []

    def popular(self) -> "Artist":
        """Popular songs for the artist

        Returns:
            Artist: Artist with items set to the popular songs only
        """
        items = get_artist_popular_songs(sp=self.sp, artist_id=self.id_)
        return Artist(id_=self.id_, _items=items)

    def all_songs(self) -> "Artist":
        """All songs by the artist

        Returns:
            Artist: Artist with items set to all of their songs
        """

        # Build album collections
        album_data = get_artist_albums(artist_id=self.id_)
        album_items = [Album.from_id(album.id) for album in album_data]
        album_collection_items = [Album(id_=album.id_) for album in album_items]
        album_collection = AlbumCollection(albums=album_collection_items)

        # Retrieve items from album collection
        if album_collection:
            track_collection = album_collection.remove_duplicates().items
        else:
            track_collection = []

        return track_collection

    def related_artists(self, n: int, include: bool = True) -> "ArtistCollection":
        """Artists related to the artist

        Args:
            n (int): The number of related artists
            include (bool): Whether the original artist should be included

        Returns:
            ArtistCollection: Collection of related artists
        """
        related_artist_items = get_related_artists(sp=self.sp, artist_id=self.id_)

        if include:
            related_artist_items.append(self)
            n += 1

        related_artists = [
            Artist(id_=artist_item.id) for artist_item in related_artist_items[:n]
        ]

        return ArtistCollection(artists=related_artists)


@dataclass
class ArtistCollection(TrackCollection):
    """Class representing a collection of artists"""

    artists: List[Artist] = field(default_factory=list)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            if self.artists:
                # Items of an ArtistCollection is the combination of the items
                # of all underlying artists
                return sum(self.artists).items
            else:
                return []

    def popular(self) -> TrackCollection:
        """Popular songs of a given artist collection

        Returns:
            TrackCollection: New collection with all popular songs
        """
        return sum([artist.popular() for artist in self.artists])


@dataclass
class AlbumCollection(TrackCollection):
    """Class representing a collection of albums"""

    albums: List[Artist] = field(default_factory=list)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            if self.albums:
                return sum(self.albums).items
            else:
                return []


class Genre(TrackCollection):
    """Class representing an genre's track contents"""

    def __init__(self, genre_name: str = "") -> None:
        self.genre_name = genre_name
        self._items = []

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            if self.id_:
                return get_recommendations_for_genre(
                    sp=self.sp, genre_names=[self.genre_name]
                )
            else:
                return []


class SavedTracks(TrackCollection):
    """Class representing an saved track contents"""

    def __init__(self) -> None:
        self._items = []

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            return get_all_saved_tracks(sp=self.sp)


class Show(TrackCollection):
    """Class representing an show's episode contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_show_id(sp=cls.sp, query=name)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            if self.id_:
                return get_show_episodes(sp=self.sp, show_id=self.id_)
            else:
                return []
