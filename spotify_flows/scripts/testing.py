import spotify_flows.spotify.collections as spocol
import spotify_flows.spotify.data_structures as ds
from spotify_flows.database import SpotifyDatabase

p = spocol.TestPlaylist.from_id("07Wq0JcPX4zVdwljPGANoT")

for item in p.items:
    print(item)

# a = ds.ArtistItem(id="test", name="test", popularity=10, genres=["hi", "no"])

# db = SpotifyDatabase("data/spotify.db", op_table="operations")
# db.add_artist(a)
