import numpy as np

def load_csv(filename):
    data = np.loadtxt(filename, delimiter=",")
    X = data[:, :-1]
    y = data[:, -1]
    return X, y

def save_model(model, filename):
    np.save(filename, model)
