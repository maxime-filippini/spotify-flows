"""
    This module is the main API used to create track collections
"""

# Standard library imports
import copy
import random
import inspect
import itertools
from typing import Any
from typing import List
from typing import Union
from typing import Tuple
from typing import Callable
from dataclasses import dataclass, field, asdict

# Third party imports
import numpy as np
import pandas as pd
import networkx as nx

# Local imports
from spotify_flows.database import SpotifyDatabase

from .login import login
from .data_structures import SpotifyDataStructure, TrackItem

from .tracks import get_track_id, read_track_from_id
from .tracks import get_audio_features
from .albums import get_album_id
from .albums import get_album_songs
from .podcasts import get_show_id
from .podcasts import get_show_episodes
from .user import get_all_saved_tracks
from .user import get_recommendations_for_genre

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

    read_items_from_db = lambda id_, db: db.build_collection_from_collection_id(id_=id_)

    sp = login(
        scope="playlist-modify-private playlist-modify-public user-read-playback-position user-library-read"
    )

    id_: str = ""
    info: SpotifyDataStructure = None
    _items: List[Any] = field(default_factory=list)
    _audio_features_enriched: bool = False

    @property
    def items(self):
        yield from self._items

    @classmethod
    def from_id(cls, id_: str):
        return cls(id_=id_, info=None)

    @classmethod
    def from_item(cls, id_: str, item: SpotifyDataStructure):
        return cls(id_=id_, info=item)

    @classmethod
    def from_db(cls, id_: str, db_path: str):
        db = SpotifyDatabase(db_path, op_table="table")
        items = cls.read_items_from_db(id_=id_, db=db)
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

        def new_items():
            yield from self.items
            yield from other.items

        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(
            id_="", _items=new_items(), _audio_features_enriched=enriched
        )

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
        other_items = list(other.items)

        def new_items():
            for item in self.items:
                if item not in other_items:
                    yield item

        enriched = self._audio_features_enriched
        return TrackCollection(
            id_="", _items=new_items(), _audio_features_enriched=enriched
        )

    def __truediv__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the division of two collections.

        Returns:
            TrackCollection: Items are intersection of self and other
        """
        other_items = list(other.items)

        def new_items():
            for item in self.items:
                if item in other_items:
                    yield item

        enriched = self._audio_features_enriched
        return TrackCollection(
            id_="", _items=new_items(), _audio_features_enriched=enriched
        )

    def __mod__(self, other: "TrackCollection") -> "TrackCollection":
        """Defines the modulo of two collections

        Returns:
            TrackCollection: Items are alternates of self and other.
        """

        def new_items():
            for i, j in zip(self.items, other.items):
                yield i
                yield j

        enriched = (self._audio_features_enriched) and (other._audio_features_enriched)
        return TrackCollection(_items=new_items(), _audio_features_enriched=enriched)

    def to_dataframes(self) -> Tuple[pd.DataFrame]:
        """Transforms items into dataframes, used for storage in database.

        Returns:
            Tuple[pd.DataFrame]: Representation of items as dataframes
        """

        # Enrich with audio features
        tracks = copy.copy(list(self.add_audio_features().items))

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
        new_items_list = copy.copy(list(self.items))
        random.shuffle(new_items_list)

        new_items = (item for item in new_items_list)

        return TrackCollection(
            _items=new_items, _audio_features_enriched=self._audio_features_enriched
        )

    def random(self, N: int) -> "TrackCollection":
        """Sample items randomly

        Args:
            N (int): Number of items to pick

        Returns:
            TrackCollection: Object with new items
        """

        def new_items():
            yield from random.sample(list(self.items), k=N)

        return TrackCollection(
            _items=new_items(), _audio_features_enriched=self._audio_features_enriched
        )

    def remove_remixes(self) -> "TrackCollection":
        """Remove remixes from items

        Returns:
            TrackCollection: Object with new items
        """
        banned_words = ["remix", "mixed"]

        def new_items():
            for item in self.items:
                if all(
                    [
                        (banned_word not in item.name.lower())
                        for banned_word in banned_words
                    ]
                ):
                    yield item

        return TrackCollection(
            _items=new_items(), _audio_features_enriched=self._audio_features_enriched
        )

    def sort(self, by: str, ascending: bool = True) -> "TrackCollection":
        """Sort items

        Args:
            by (str): Criteria used for sorting
            ascending (bool, optional): Ascending order. Defaults to True.

        Returns:
            TrackCollection: Object with sorted items
        """
        str_attr = f"item.{by}"

        def new_items():
            # Enrichment with audio features if needed
            if by.startswith("audio_features") and not self._audio_features_enriched:
                all_items = self._enrich_with_audio_features(items=self.items)
                self._audio_features_enriched = True

            else:
                all_items = self.items

            sorted_items = sorted(
                list(all_items),
                key=eval(f"lambda item: {str_attr}"),
                reverse=(not ascending),
            )

            yield from sorted_items

        return TrackCollection(
            _items=new_items(), _audio_features_enriched=self._audio_features_enriched
        )

    def filter(self, criteria_func: Callable[..., Any]) -> "TrackCollection":
        """Filter items by certain criteria function

        Args:
            criteria_func (Callable[..., Any]): Criteria used for filtering

        Returns:
            TrackCollection: Object with filtered items
        """

        # Enrichment with audio features if needed
        def new_items():

            if (
                "audio_features" in inspect.getsource(criteria_func)
                and not self._audio_features_enriched
            ):
                self._audio_features_enriched = True
                all_items = self._enrich_with_audio_features(items=self.items)

            else:
                all_items = self.items

            for item in all_items:
                if criteria_func(item):
                    yield item

        return TrackCollection(
            _items=new_items(), _audio_features_enriched=self._audio_features_enriched
        )

    def trim_duration(self, minutes: Union[int, Tuple[int, int]]):
        items = copy.copy(self.items)
        cum_time = np.cumsum(np.array([item.duration_ms for item in items])) / 1000 / 60

        if isinstance(minutes, int):
            n_below = len(cum_time[cum_time <= minutes])
            trim_points = (0, n_below)
        else:
            n_below_min = len(cum_time[cum_time <= minutes[0]])
            n_below_max = len(cum_time[cum_time <= minutes[1]])
            trim_points = (n_below_min + 1, n_below_max)

        new_items = items[trim_points[0] : trim_points[1] + 1]
        return TrackCollection(_items=(i for i in new_items))

    def add_audio_features(self) -> "TrackCollection":
        def new_items():
            for item in self.items:
                item.audio_features = get_audio_features(track_ids=[item.id])[item.id]
                yield item

        return TrackCollection(_items=new_items(), _audio_features_enriched=True)

    def _enrich_with_audio_features(self, items: List[TrackItem]) -> List[TrackItem]:
        """Get items enriched with audio features

        Args:
            items (List[TrackItem]): Items to enrich

        Returns:
            List[TrackItem]: Enriched items
        """
        for item in items:
            item.audio_features = get_audio_features(track_ids=[item.id])[item.id]
            yield item

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

        new_coll = copy.deepcopy(self)
        new_coll._items = items
        return new_coll

    def first(self, n: int) -> "TrackCollection":
        """First n items

        Returns:
            TrackCollection: Collection with trimmed items
        """

        new_items = itertools.islice(self.items, n)

        return TrackCollection(
            _items=new_items, _audio_features_enriched=self._audio_features_enriched
        )

    def to_playlist(self, playlist_name: str) -> None:
        if playlist_name is None:
            playlist_name = self.id_
        make_new_playlist(sp=self.sp, playlist_name=playlist_name, items=self.items)

    def to_database(self, db: SpotifyDatabase) -> None:
        db.store_tracks_in_database(collection=self)

    def optimize(self, target_func, N: int = 1) -> None:
        items = list(self.items)
        diffs = np.abs(np.array([target_func(item) for item in items]))
        idx = np.argsort(diffs)
        n = min(N, len(items))
        return TrackCollection(_items=list(np.array(items)[idx[:n]]))

    def complex_sort(
        self, by: str = "artist", graph: nx.Graph = nx.Graph()
    ) -> "TrackCollection":
        items = list(self.items)

        def new_items():
            unique_artists = list(set([item.album.artists[0].id for item in items]))

            artists = [
                (
                    artist_id,
                    [item for item in items if item.album.artists[0].id == artist_id],
                )
                for artist_id in unique_artists
            ]

            remaining_artists = artists
            latest_artist = remaining_artists.pop(0)

            new_items_ = [track for track in latest_artist[1]]

            while remaining_artists:
                # Find the closest artist

                all_path_lengths = []

                for artist in remaining_artists:
                    try:
                        path_length = nx.shortest_path_length(
                            graph,
                            source=latest_artist[0],
                            target=artist[0],
                            weight="weight",
                        )
                    except nx.NetworkXNoPath as e:
                        path_length = 9999999

                    all_path_lengths.append(path_length)

                # Get the minimum
                all_path_lengths = np.array(all_path_lengths)
                min_idx = np.where(all_path_lengths == all_path_lengths.min())[0][0]

                # Set the latest artist
                latest_artist = remaining_artists.pop(min_idx)

                # Add the tracks
                new_items_ += [track for track in latest_artist[1]]

            return (item for item in new_items_)

        return TrackCollection(
            _items=new_items(), _audio_features_enriched=self._audio_features_enriched
        )


@dataclass
class Playlist(TrackCollection):
    """Class representing a Playlist's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_playlist_id(sp=cls.sp, playlist_name=name)

    @property
    def items(self):
        if self._items:
            yield from self._items
        else:
            if self.id_:
                yield from get_playlist_tracks(sp=self.sp, playlist_id=self.id_)

            else:
                yield from iter(())


class Album(TrackCollection):
    """Class representing an Album's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_album_id(sp=cls.sp, album_name=name)

    @property
    def items(self):
        if self._items:
            yield from self._items
        else:
            if self.id_:
                yield from get_album_songs(sp=self.sp, album_id=self.id_)
            else:
                yield from iter(())


class Artist(TrackCollection):
    """Class representing an Artist's track contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_artist_id(sp=cls.sp, artist_name=name)

    @property
    def items(self):
        if self._items:
            yield from self._items
        else:
            if self.id_:
                yield from self.all_songs()
            else:
                yield from iter(())

    def popular(self) -> "Artist":
        """Popular songs for the artist

        Returns:
            Artist: Artist with items set to the popular songs only
        """

        def items():
            yield from get_artist_popular_songs(sp=self.sp, artist_id=self.id_)

        return Artist(id_=self.id_, _items=items())

    def all_songs(self) -> "Artist":
        """All songs by the artist

        Returns:
            Artist: Artist with items set to all of their songs
        """

        # Build album collections
        album_data = get_artist_albums(artist_id=self.id_)
        album_collection_items = [Album.from_id(album.id) for album in album_data]
        album_collection = CollectionCollection(collections=album_collection_items)

        # Retrieve items from album collection
        if album_collection:
            yield from album_collection.items

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

        return ArtistCollection(collections=related_artists)


@dataclass
class CollectionCollection(TrackCollection):
    collections: List[TrackCollection] = field(default_factory=list)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            items_to_load = self._items
        else:
            if self.collections:
                items_to_load = sum(self.collections).items
            else:
                items_to_load = iter(())

        yield from items_to_load

    def alternate(self):
        def new_items():
            return itertools.chain(*zip(*[c.items for c in self.collections]))

        return TrackCollection(id_="", _items=new_items())


@dataclass
class ArtistCollection(CollectionCollection):
    """Class representing a collection of artists"""

    collections: List[Artist] = field(default_factory=list)

    def popular(self) -> TrackCollection:
        """Popular songs of a given artist collection

        Returns:
            TrackCollection: New collection with all popular songs
        """
        return sum([artist.popular() for artist in self.collections])


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
                yield from get_recommendations_for_genre(
                    sp=self.sp, genre_names=[self.genre_name]
                )
            else:
                yield from iter(())


class SavedTracks(TrackCollection):
    """Class representing an saved track contents"""

    def __init__(self) -> None:
        self._items = []

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            return self._items
        else:
            yield from get_all_saved_tracks(sp=self.sp)


class Show(TrackCollection):
    """Class representing an show's episode contents"""

    @classmethod
    def func_get_id(cls, name):
        return get_show_id(sp=cls.sp, query=name)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            yield from self._items
        else:
            if self.id_:
                yield from get_show_episodes(sp=self.sp, show_id=self.id_)
            else:
                yield from iter(())


class Track(TrackCollection):
    """Class representing a single-track collection"""

    @classmethod
    def func_get_id(cls, name):
        return get_track_id(sp=cls.sp, track_name=name)

    @property
    def items(self) -> List[TrackItem]:
        if self._items:
            yield from self._items
        else:
            if self.id_:
                yield read_track_from_id(track_id=self.id_)
            else:
                yield None
