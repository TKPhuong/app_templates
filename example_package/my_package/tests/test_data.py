from my_package.models.models.data import X, y

def test_data():
    assert X.shape == (3, 2)
    assert y.shape == (3,)
