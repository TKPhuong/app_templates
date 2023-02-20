from models.linear_regression import LinearRegression
from models.data import X, y
from utils.math import mean_squared_error

model = LinearRegression()
model.fit(X, y)

y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

print(f"Coefficients: {model.coef_}")
print(f"Mean squared error: {mse:.2f}")