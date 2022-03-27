from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
import numpy as np


class Classifier(BaseEstimator):
    def __init__(self):
        self.preprocessor = MinMaxScaler()
        self.classifier_1 = RandomForestClassifier()
        self.classifier_2 = MLPClassifier(solver='lbfgs', alpha=1e-7,
                        hidden_layer_sizes=(40, 2), random_state=1)

        self.model_1 = Pipeline([('scaler', self.preprocessor), ('classifier', self.classifier_1)])
        self.model_2 = Pipeline([('scaler', self.preprocessor), ('classifier', self.classifier_2)])

    def fit(self, X, Y):

        self.model_1.fit(X, Y)
        self.model_2.fit(X, Y)

    def predict(self, X):
        res_1 = self.model_1.predict(X)
        res_2 = self.model_2.predict(X)
        res = np.concatenate((res_1, res_2)).reshape(2, res_vac.shape[0])

        return res
