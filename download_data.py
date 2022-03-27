import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

client_id = "908dd70b4a2b4bdd87e502cc22012572"
client_secret = "7d8d1ec41d414694aa30fc606ce74a43"

auth_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
sp = spotipy.Spotify(auth_manager=auth_manager)


def flatten(lists):
    return [element for list_ in lists for element in list_]


def get_playlist_musics(playlist_id):

    playlist_uri = f"spotify:playlist:{playlist_id}"

    def get_musics(offset):
        options = {"limit": 100, "offset": offset}
        return sp.playlist_tracks(playlist_uri, **options)["items"]

    # get the number of tracks in the playlist
    nb_tracks = sp.playlist(playlist_uri)["tracks"]["total"]

    # get the playlist musics with the api
    list_musics = [get_musics(offset) for offset in tqdm(range(0, nb_tracks, 100))]
    # flatten the list
    list_musics = [music["track"] for musics in list_musics for music in musics]

    return list_musics


def get_playlist_list_musics(lst_playlist_id):

    list_music = []
    for playlist_id in lst_playlist_id:
        list_music.append(get_playlist_musics(playlist_id))

    return flatten(list_music)


def parse_musics(list_musics, max_nb_artists):

    meta_musics = []

    for music in list_musics:
        # check if the uri of the music is in the good format
        if not music["uri"].startswith("spotify:track:"):
            continue

        metadonnee = []

        metadonnee.append(music["uri"])
        metadonnee.append(music["name"])

        metadonnee.append(music["duration_ms"])
        metadonnee.append(music["popularity"])
        metadonnee.append(music["explicit"])

        # get all the artist in the music :
        nb_artists = len(music["artists"])
        metadonnee.append(nb_artists)

        for i, artist in enumerate(music["artists"]):
            if i > (max_nb_artists - 1):
                break
            metadonnee.append(artist["name"])
            metadonnee.append(artist["uri"])
        # padding
        for _ in range(max_nb_artists - (i + 1)):
            metadonnee.append(np.NaN)
            metadonnee.append(np.NaN)

        metadonnee.append(music["album"]["name"])
        metadonnee.append(music["album"]["release_date"])

        metadonnee.append(music["preview_url"])
        meta_musics.append(metadonnee)

    return meta_musics


def get_audio_features(list_musics_uri):
    nb_tracks = len(list_musics_uri)

    audio_features = [
        sp.audio_features(list_musics_uri[i : i + 100])
        for i in tqdm(range(0, nb_tracks, 100))
    ]
    # flatten the list
    audio_features = flatten(audio_features)

    return audio_features


def get_artists(list_artists):
    nb_artists = len(list_artists)
    artists_data = [
        sp.artists(list_artists[i : i + 50]) for i in tqdm(range(0, nb_artists, 50))
    ]

    # flatten list
    artists_data = [artist for artists in artists_data for artist in artists["artists"]]
    return artists_data


def parse_artists(artists_data, max_nb_genres):
    meta = []

    for artist in artists_data:
        metadonnee = []

        metadonnee.append(artist["uri"])
        metadonnee.append(artist["popularity"])

        i = 0
        while (i < len(artist["genres"])) & (i < (max_nb_genres - 1)):
            metadonnee.append(artist["genres"][i])
            i += 1
        for _ in range(max_nb_genres - i):
            metadonnee.append(np.NaN)

        meta.append(metadonnee)
    return meta


def get_df_from_playlist(list_playlist_id, max_nb_artists=None):

    assert isinstance(list_playlist_id, list), 'The input must be a list'
    
    # get all musics from playlist
    print('Getting playlists...')
    list_musics = get_playlist_list_musics(list_playlist_id)
    list_musics = list(filter(None, list_musics))

    # set the maximum of artists listed for one track
    if max_nb_artists is None:
        max_nb_artists = max([len(music["artists"]) for music in list_musics])

    # create artist name columns based on max_nb_artists
    artists_columns = [
        [f"artist_name_{i+1}", f"artist_uri_{i+1}"] for i in range(max_nb_artists)
    ]
    artists_columns = [element for tuples in artists_columns for element in tuples]

    columns_name_meta = [
        "uri",
        "name",
        "duration_ms",
        "popularity",
        "explicit",
        "nb_artist",
        *artists_columns,
        "album_name",
        "album_date",
    ]

    # parse the results from the api and create a dataframe
    list_meta = parse_musics(list_musics, max_nb_artists)
    df_music = pd.DataFrame(list_meta, columns=columns_name_meta)

    # drop duplicate 
    df_music = df_music.drop_duplicates()

    # get all the info on every music
    print('Getting audio features...')
    audio_features = get_audio_features(df_music.uri.values)

    columns_name_audio = [
        "uri",
        "danceability",
        "energy",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]

    # filter musics without audio features and create dataframe
    df_audio_features = pd.DataFrame(filter(None, audio_features))
    df_audio = df_audio_features[columns_name_audio]

    # merge the two dataframes
    return df_music.merge(df_audio, on='uri')