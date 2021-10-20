import pytest
import hypothesis

import spotify_flows.spotify.collections as spocol

collection_classes = [
    spocol.TrackCollection,
    spocol.Artist,
    spocol.Album,
    spocol.Playlist,
    spocol.Genre,
    spocol.ArtistCollection,
    spocol.AlbumCollection,
]


@pytest.mark.parametrize("cls", collection_classes)
def test_empty(cls):
    assert len(cls().items) == 0


def test_return_types():
    col = spocol.Artist()
    assert isinstance(col, spocol.TrackCollection)

    col = col + spocol.Album()
    assert isinstance(col, spocol.TrackCollection)

    col = col % spocol.Playlist()
    assert isinstance(col, spocol.TrackCollection)

    col = col - spocol.Genre()
    assert isinstance(col, spocol.TrackCollection)
