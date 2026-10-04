import pandas as pd
import numpy as np


def load_nasa_data(file_path):
    """Load NASA POWER daily weather data."""

    data = pd.read_csv(
        file_path,
        skiprows=11
    )

    return data


def clean_nasa_data(data):
    """Clean and organize NASA weather data."""

    data = data.copy()

    # Remove duplicate rows
    data = data.drop_duplicates()

    # Replace invalid values with NaN
    data = data.replace(
        [-999, np.inf, -np.inf],
        np.nan
    )

    # Keep only the weather columns required for our project
    required_columns = [
        "YEAR",
        "DOY",
        "T2M",
        "RH2M",
        "PRECTOTCORR"
    ]

    data = data[required_columns]

    # Rename columns
    data = data.rename(
        columns={
            "YEAR": "year",
            "DOY": "day_of_year",
            "T2M": "temperature",
            "RH2M": "humidity",
            "PRECTOTCORR": "rainfall"
        }
    )

    # Convert weather columns to numeric
    numeric_columns = [
        "temperature",
        "humidity",
        "rainfall"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Fill missing values with median
    for column in numeric_columns:
        data[column] = data[column].fillna(
            data[column].median()
        )

    return data


def save_processed_data(data, output_path):
    """Save processed weather data."""

    data.to_csv(
        output_path,
        index=False
    )

    print(
        f"Processed data saved to: {output_path}"
    )


def preprocess_nasa_data(input_path, output_path):
    """Complete NASA data preprocessing pipeline."""

    data = load_nasa_data(input_path)

    print("NASA data loaded successfully.")
    print(f"Original rows: {len(data)}")

    data = clean_nasa_data(data)

    print("NASA data cleaned successfully.")
    print(f"Processed rows: {len(data)}")

    save_processed_data(
        data,
        output_path
    )


if __name__ == "__main__":

    input_file = (
        "data/raw/"
        "POWER_Point_Daily_20200101_20261004_"
        "012d90N_074d76E_LST.csv"
    )

    output_file = (
        "data/processed/"
        "processed_weather_data.csv"
    )

    preprocess_nasa_data(
        input_file,
        output_file
    )