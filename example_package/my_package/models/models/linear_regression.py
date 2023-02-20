import numpy as np
from utils.math import mean_squared_error

class LinearRegression:
    def __init__(self):
        self.coef_ = None

    def fit(self, X, y):
        X = np.hstack([X, np.ones((X.shape[0], 1))])
        self.coef_ = np.linalg.inv(X.T @ X) @ X.T @ y

    def predict(self, X):
        X = np.hstack([X, np.ones((X.shape[0], 1))])
        y_pred = X @ self.coef_
        return y_pred
