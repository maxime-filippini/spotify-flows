"""
    This module holds the API functions related to album information
"""

# Standard library imports

# Third party imports
from spotipy import Spotify

# Local imports

# Main body
class ExtendedSpotify(Spotify):
    def playlist_add_episodes(self, playlist_id, items, position=None):
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("episode", tid) for tid in items]
        return self._post(
            "playlists/%s/tracks" % (plid), payload=ftracks, position=position
        )

    def playlist_remove_episodes(self, playlist_id, items):
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("episode", tid) for tid in items]
        payload = {"tracks": [{"uri": track} for track in ftracks]}

        return self._delete("playlists/%s/tracks" % (plid), payload=payload)
