import os
import pandas as pd
import numpy as np
import rampwf as rw
from sklearn.model_selection import ShuffleSplit


problem_title = 'Spotify Popularity'

_prediction_label_name = [0, 1]

Predictions = rw.prediction_types.make_multiclass(
    label_names=_prediction_label_name
)
workflow = rw.workflows.Classifier()

score_types = [
    rw.score_types.ROCAUC(name='auc'),
    rw.score_types.Accuracy(name='acc'),
    rw.score_types.NegativeLogLikelihood(name='nll'),
]


def get_cv(X, y):
    cv = ShuffleSplit(n_splits=8, test_size=0.2, random_state=42)
    return cv.split(X, y)


def _get_data(path='data', fname):
    data_path = os.path.join(path, fname)

    df = pd.read_csv(data_path, low_memory=False)

    X = df.drop(['popularity', 'is_top50'], axis=1)
    y = df[['is_top50']]

    return X, y


def get_train_data(path):
    return _get_data(path, 'train.csv')


def get_test_data(path):
    return _get_data(path, 'test.csv')
