
def calculate_water_requirement(
    crop_water_requirement,
    cultivated_area,
    effective_rainfall
):
    """
    Calculate seasonal irrigation water volume.

    crop_water_requirement: mm per growing season
    cultivated_area: hectares
    effective_rainfall: mm per growing season

    Returns irrigation requirement in cubic metres.
    """

    if crop_water_requirement < 0:
        raise ValueError("Crop water requirement cannot be negative.")

    if cultivated_area <= 0:
        raise ValueError("Cultivated area must be greater than zero.")

    if effective_rainfall < 0:
        raise ValueError("Rainfall cannot be negative.")

    net_water_depth = max(
        crop_water_requirement - effective_rainfall,
        0
    )

    irrigation_volume = (
        net_water_depth * cultivated_area * 10
    )

    return irrigation_volume


def estimate_water_demand(
    crop,
    crop_water_requirement,
    cultivated_area,
    effective_rainfall
):
    irrigation_requirement = calculate_water_requirement(
        crop_water_requirement,
        cultivated_area,
        effective_rainfall
    )

    return {
        "crop": crop,
        "water_requirement_mm": crop_water_requirement,
        "cultivated_area_hectares": cultivated_area,
        "effective_rainfall_mm": effective_rainfall,
        "irrigation_requirement_m3": round(
            irrigation_requirement, 2
        )
    }


def compare_water_requirements(crop_data):
    results = []

    for crop in crop_data:
        result = estimate_water_demand(
            crop=crop["crop"],
            crop_water_requirement=crop["crop_water_requirement"],
            cultivated_area=crop["cultivated_area"],
            effective_rainfall=crop["effective_rainfall"]
        )

        results.append(result)

    results.sort(
        key=lambda item: item["irrigation_requirement_m3"]
    )

    return results


if __name__ == "__main__":

    result = estimate_water_demand(
        crop="Rice",
        crop_water_requirement=1200,
        cultivated_area=1,
        effective_rainfall=500
    )

    print("Crop:", result["crop"])
    print(
        "Irrigation Requirement:",
        result["irrigation_requirement_m3"],
        "m³"
    )
