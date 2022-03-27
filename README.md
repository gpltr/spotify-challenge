# Spotify Datacamp

## Documentation

Document about spotipy and spotify API

[Documentation](https://spotipy.readthedocs.io/en/2.19.0/)


[Spotify API](https://developer.spotify.com/documentation/web-api/reference/#/)
## Installation

```bash
pip install spotipy
```

or upgrade

```bash
pip install spotipy --upgrade
```

## Quick Start
Load all the imports :
```bash
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd
import utils_api as api

from tqdm import tqdm
```

To get started, install spotipy and create an app on https://developers.spotify.com/.
Add your new ID and SECRET to your environment:



```python
client_id = "APP_CLIENT_ID"
client_secret = "APP_CLIENT_SECRET"

auth_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
sp = spotipy.Spotify(auth_manager=auth_manager)
```

## Create the dataframes
```python
list_playlist_id = ["69fEt9DN5r4JQATi52sRtq",
                    "5S8SJdl1BDc0ugpkEvFsIL",
                    "6yPiKpy7evrwvZodByKvM9",
                    "4rnleEAOdmFAbRcNCgZMpY",
                    "6iaALa2quWaw2Wg4SvlS5y",
                    "6FKDzNYZ8IW1pvYVF4zUN2",
                    "6WMgB51Ys7GWuBwDpXS2pK",
                    "1G8IpkZKobrIlXcVPoSIuf"]

df_music = api.get_df_from_playlist(list_playlist_id)
```
```python
uri_artists = [col for col in df_music if col.startswith('artist_uri')]

all_artists = df_music[uri_artists].values.flatten()
# remove duplicate
list_artists = list(set(filter(lambda x: x != "nan", all_artists.astype("str"))))

artists_data = api.get_artists(list_artists)
```
```python
# max number of genres for each artists
max_nb_genres = max([len(artist["genres"]) for artist in artists_data])

artists_meta = api.parse_artists(artists_data, max_nb_genres)

columns_name_artists = ["artist_uri", "artist_popularity"] + [
    f"genre_artist_{i}" for i in range(max_nb_genres)
]

df_artist = pd.DataFrame(artists_meta, columns=columns_name_artists)
```
```python
df_artist.to_csv('df_artist.csv')
df_music.to_csv('df_music.csv')
df = pd.read_csv('./demo_spotify_30k.csv', sep = '|')
```
