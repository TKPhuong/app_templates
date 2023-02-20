from my_package.utils.utils.math import mean_squared_error
import numpy as np

def test_mean_squared_error():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([2, 3, 4])
    mse = mean_squared_error(y_true, y_pred)
    assert mse == 1.0
