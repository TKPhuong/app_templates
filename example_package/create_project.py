import os

# Define the directory structure
dir_structure = {
    "my_package": {
        "__init__.py": "",
        "setup.py": "",
        "tests": {
            "test_data.py": "",
            "test_linear_regression.py": "",
            "test_math.py": "",
            "test_io.py": "",
        },
        "utils": {
            "__init__.py": "",
            "setup.py": "",
            "math.py": "",
            "io.py": "",
        },
        "models": {
            "__init__.py": "",
            "setup.py": "",
            "data.py": "",
            "linear_regression.py": "",
        },
        "README.md": "",
    }
}

# Define the contents of each file
file_contents = {
    "my_package/__init__.py": "",
    "my_package/setup.py": """from setuptools import setup, find_packages

setup(
    name="my_package",
    version="1.0.0",
    description="A package for linear regression",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    test_suite="tests",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
""",
    "my_package/tests/test_data.py": """from my_package.models.data import X, y

def test_data():
    assert X.shape == (3, 3)
    assert y.shape == (3,)
""",
    "my_package/tests/test_linear_regression.py": """from my_package.models.linear_regression import LinearRegression
from my_package.models.data import X, y

def test_linear_regression():
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == (3,)
""",
    "my_package/tests/test_math.py": """from my_package.utils.math import mean_squared_error

def test_mean_squared_error():
    y_true = [1, 2, 3, 4]
    y_pred = [2, 3, 4, 5]
    mse = mean_squared_error(y_true, y_pred)
    assert mse == 1.0
""",
    "my_package/tests/test_io.py": """from my_package.utils.io import load_csv

def test_load_csv():
    X, y = load_csv("test.csv")
    assert X.shape == (3, 2)
    assert y.shape == (3,)
""",
    "my_package/utils/__init__.py": "",
    "my_package/utils/setup.py": """from setuptools import setup, find_packages

setup(
    name="my_package_utils",
    version="1.0.0",
    description="Utility functions for linear regression",
    packages=find_packages(),
)
""",
    "my_package/utils/math.py": """import numpy as np

def mean_squared_error(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)
    return mse
""",
    "my_package/utils/io.py": """import numpy as np

def load_csv(filename):
    data = np.loadtxt(filename, delimiter=",")
    X = data[:, :-1]
    y = data[:, -1]
    return X, y

def save_model(model, filename):
    np.save(filename, model)
""",
    "my_package/models/__init__.py": "",
    "my_package/models/setup.py": """from setuptools import setup, find_packages

setup(
    name="my_package_models",
    version="1.0.0",
    description="Linear regression models",
    packages=find_packages(),
)
""",
    "my_package/models/data.py": """import numpy as np


X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([2, 5, 8])
""",
    "my_package/models/linear_regression.py": """import numpy as np
from my_package.utils.math import mean_squared_error

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
""",
    "my_package/README.md": "",
}

# Create the directory structure and write file contents
for path, content in file_contents.items():
    full_path = os.path.join(*path.split("/"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Package directory structure created successfully!")