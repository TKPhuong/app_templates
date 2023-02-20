import os
import numpy as np
from my_package.utils.utils.io import load_csv

def test_load_csv():
    data = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
    filename = "test.csv"
    np.savetxt(filename, data, delimiter=",")
    X, y = load_csv(filename)
    os.remove(filename)
    assert X.shape == (3, 3)
    assert y.shape == (3,)
