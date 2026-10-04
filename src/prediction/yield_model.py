import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


def train_yield_model(data):
    """
    Train a crop yield prediction model.

    Required columns:
    soil_type
    rainfall
    temperature
    crop_type
    yield
    """

    required_columns = [
        "soil_type",
        "rainfall",
        "temperature",
        "crop_type",
        "yield"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {', '.join(missing_columns)}"
        )

    X = data[
        ["soil_type", "rainfall", "temperature", "crop_type"]
    ]

    y = data["yield"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    categorical_columns = ["soil_type", "crop_type"]
    numerical_columns = ["rainfall", "temperature"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_columns
            ),
            (
                "numerical",
                "passthrough",
                numerical_columns
            )
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                )
            )
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("Yield Prediction Model trained successfully.")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"R² Score: {r2:.2f}")

    return model


def predict_yield(model, soil_type, rainfall, temperature, crop_type):
    """
    Predict crop yield for a given set of conditions.
    """

    input_data = pd.DataFrame({
        "soil_type": [soil_type],
        "rainfall": [rainfall],
        "temperature": [temperature],
        "crop_type": [crop_type]
    })

    prediction = model.predict(input_data)

    return prediction[0]


def save_model(model, model_path):
    """Save the trained model."""
    joblib.dump(model, model_path)
    print(f"Yield model saved to: {model_path}")


def load_model(model_path):
    """Load a saved yield model."""
    return joblib.load(model_path)