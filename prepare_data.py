import pandas as pd
from sklearn.model_selection import train_test_split
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import utils_api as api
import download_data as dw_data
from pathlib import Path

# To re fetch the data you need to set CLIENT_ID and CLIENT_SECRET in the 
# utils_api file and set REFETCH to True
CLIENT_ID = None
CLIENT_SECRET = None
REFETCH = False

LOCAL_DATA = Path(__file__).parent / "data"


def refetch_data(sp):
    # List of playlist ids used to create the dataset 
    list_playlist_id = ["69fEt9DN5r4JQATi52sRtq",
                        "5S8SJdl1BDc0ugpkEvFsIL",
                        "6yPiKpy7evrwvZodByKvM9",
                        "4rnleEAOdmFAbRcNCgZMpY",
                        "6iaALa2quWaw2Wg4SvlS5y",
                        "6FKDzNYZ8IW1pvYVF4zUN2",
                        "6WMgB51Ys7GWuBwDpXS2pK",
                        "1G8IpkZKobrIlXcVPoSIuf"]

    #### Download the musics ####

    df_music = api.get_df_from_playlist(sp, list_playlist_id)

    #### Get the artists ####

    uri_artists = [col for col in df_music if col.startswith('artist_uri')]
    all_artists = df_music[uri_artists].values.flatten()
    # remove duplicate
    list_artists = list(set(filter(lambda x: x != "nan", 
                                   all_artists.astype("str"))))

    artists_data = api.get_artists(sp, list_artists)

    #### Get the genres for each artists ####

    # max number of genres for each artists
    max_nb_genres = max([len(artist["genres"]) for artist in artists_data])

    artists_meta = api.parse_artists(artists_data, max_nb_genres)

    columns_name_artists = ["artist_uri", "artist_popularity"] + [
        f"genre_artist_{i}" for i in range(max_nb_genres)
    ]

    df_artist = pd.DataFrame(artists_meta, columns=columns_name_artists)

    # Save the data
    df_artist.to_csv(os.path.join(LOCAL_DATA, 'df_artist.csv'), index=False)
    df_music.to_csv(os.path.join(LOCAL_DATA, 'df_music.csv'), index=False)


if __name__ == '__main__':
    # 1 - Read or download the data
    # If the data is not already in the folder we download them or refetch them
    no_data_folder = (not LOCAL_DATA.exists() or not any(LOCAL_DATA.iterdir()))
    no_csv_files = (not any(fname.endswith('.csv') for fname in os.listdir(LOCAL_DATA)))

    if no_data_folder or no_csv_files:
        if REFETCH:
            assert CLIENT_ID is not None, 'You need to set the spotify logins'
            auth_manager = SpotifyClientCredentials(
                client_id=CLIENT_ID, client_secret=CLIENT_SECRET
            )
            sp = spotipy.Spotify(auth_manager=auth_manager)

            refetch_data(sp)
        else:
            dw_data.download_from_osf()

    # 2 - Splitting the dataset music (the artists dataset is shared)
    # This may be a problem as the artist may lead to data leaking but we did
    # not see how to do it overwise
    df_music = pd.read_csv(os.path.join(LOCAL_DATA, 'df_music.csv'), 
                           low_memory=False)
    df_public, _ = train_test_split(df_music, test_size=0.2, random_state=42)

    # 3 - Split public train/test subsets
    df_public_train, df_public_test = train_test_split(
        df_public, test_size=0.2, random_state=42
    )
    os.makedirs(os.path.join(LOCAL_DATA, 'public'))
    df_public_train.to_csv(os.path.join(LOCAL_DATA, 'public', 'train.csv'), index=False)
    df_public_test.to_csv(os.path.join(LOCAL_DATA, 'public', 'test.csv'), index=False)