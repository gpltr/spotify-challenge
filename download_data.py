"""Fetcher for RAMP data stored in OSF
To adapt it for another challenge, change the CHALLENGE_NAME and upload
public/private data as `tar.gz` archives in dedicated OSF folders named after
the challenge.
"""
import tarfile
import argparse
from pathlib import Path
from osfclient.api import OSF
import os

import pandas as pd

LOCAL_DATA = Path(__file__).parent / "data"

CHALLENGE_NAME = 'spotify_challenge'
# you might choosing checking for the correct checksum, if not set
# data_checksum to None
RAMP_FOLDER_CONFIGURATION = {
    'public': dict( 
        code="wje7s",
        file_name='data_spotify.tar.gz', 
    ),
}


def load_clean_data(fname):
    fname = os.path.join(LOCAL_DATA, fname)
    df = pd.read_csv(fname, encoding='iso-8859-1', na_values= ' ')
    return df


def get_connection_info():
    "Get connection to OSF and info relative to data."
    osf, folder_name = OSF(), 'public'
    data_config = RAMP_FOLDER_CONFIGURATION[folder_name]
    project = osf.project(data_config['code'])
    store = project.storage('osfstorage')
    return store, data_config


def get_data_from_osf(container):
    "Get data from OSF container with a comprehensible failure error."
    elements = [f for f in container]
    assert len(elements) == 1, (
        'There is no element in osf storage' 
    )
    return elements[0]


def download_from_osf():
    "Download the data from OSF."
    
    # create the data folder if it does not exist
    if not LOCAL_DATA.exists() or not any(LOCAL_DATA.iterdir()):
        LOCAL_DATA.mkdir(exist_ok=True)

    # check if data directory does not have .csv
    if not any(fname.endswith('.csv') for fname in os.listdir(LOCAL_DATA)):

        print("Checking the data URL...")
        # Get the connection to OSF
        store, data_config = get_connection_info()

        # -------------------------------------------------------
        # DATA SET (ALL)
        # -------------------------------------------------------

        # Find the file to download from the OSF project
        challenge_file = get_data_from_osf(store.files)

        # Find the file to download from the OSF project
        file_name = data_config['file_name']
        print('Ok.')

        # Download the file in the data
        FILE_PATH = os.path.join(LOCAL_DATA, file_name)
        print("Downloading the data...")
        with open(FILE_PATH, 'wb') as f:
            challenge_file.write_to(f)

        # Decompress the archive
        with tarfile.open(FILE_PATH, 'r:gz') as tar:
            tar.extractall(LOCAL_DATA)
        os.remove(FILE_PATH)

    else:
        print(f'{LOCAL_DATA} directory contains .csv files. Please empty it or select'
              ' another destination for LOCAL_DATA if you wish to proceed')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f'Data loader for the {CHALLENGE_NAME} challenge on RAMP.'
    )
    download_from_osf()