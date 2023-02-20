from my_package.models.models.linear_regression import LinearRegression
from my_package.models.models.data import X, y

def test_linear_regression():
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == (3,)
