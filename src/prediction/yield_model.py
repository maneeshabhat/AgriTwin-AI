
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


DATA_PATH = "data/raw/crop-yield.csv"
MODEL_PATH = "models/yield_model.joblib"


def load_crop_data(file_path=DATA_PATH):
    """Load and validate the crop yield dataset."""

    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()

    target = "Crop_Yield_ton_per_hectare"

    if target not in data.columns:
        raise ValueError(f"Target column '{target}' not found.")

    data[target] = pd.to_numeric(data[target], errors="coerce")
    data = data.dropna(subset=[target])

    if data.empty:
        raise ValueError("No valid crop-yield records found.")

    return data


def train_yield_model(data):
    """Train a crop-yield regression model."""

    target = "Crop_Yield_ton_per_hectare"

    # Features available before predicting crop yield.
    feature_columns = [
        "N",
        "P",
        "K",
        "Soil_pH",
        "Soil_Moisture",
        "Soil_Type",
        "Organic_Carbon",
        "Temperature",
        "Humidity",
        "Rainfall",
        "Sunlight_Hours",
        "Wind_Speed",
        "Region",
        "Altitude",
        "Season",
        "Crop_Type",
        "Irrigation_Type",
        "Fertilizer_Used",
        "Pesticide_Used",
    ]

    missing = [
        column for column in feature_columns + [target]
        if column not in data.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    X = data[feature_columns].copy()
    y = data[target].copy()

    categorical = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    numerical = [
        column for column in X.columns
        if column not in categorical
    ]

    for column in numerical:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, numerical),
        ("categorical", categorical_pipeline, categorical)
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("Yield model trained successfully.")
    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")
    print(f"Mean Absolute Error: {mae:.3f} tonnes/hectare")
    print(f"R² Score: {r2:.3f}")

    return model


def save_model(model, model_path=MODEL_PATH):
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")


def load_model(model_path=MODEL_PATH):
    return joblib.load(model_path)


def predict_yield(model, input_data):
    """Predict yield from a dictionary of feature values."""

    input_frame = pd.DataFrame([input_data])
    return float(model.predict(input_frame)[0])


if __name__ == "__main__":
    crop_data = load_crop_data()
    trained_model = train_yield_model(crop_data)
    save_model(trained_model)

    print("\nSample dataset records:")
    print(crop_data.head(3).to_string(index=False))
