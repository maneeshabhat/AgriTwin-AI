def calculate_water_requirement(
    crop_water_requirement,
    cultivated_area,
    rainfall
):
    """
    Estimate the water requirement for a crop.

    crop_water_requirement: water required per unit area
    cultivated_area: cultivated area
    rainfall: effective rainfall contribution
    """

    total_crop_water = (
        crop_water_requirement * cultivated_area
    )

    effective_rainfall = rainfall * cultivated_area

    irrigation_requirement = (
        total_crop_water - effective_rainfall
    )

    # Water requirement cannot be negative
    irrigation_requirement = max(
        irrigation_requirement,
        0
    )

    return irrigation_requirement


def estimate_water_demand(
    crop,
    crop_water_requirement,
    cultivated_area,
    rainfall
):
    """
    Return water-demand information for a crop.
    """

    irrigation_requirement = calculate_water_requirement(
        crop_water_requirement,
        cultivated_area,
        rainfall
    )

    return {
        "crop": crop,
        "water_requirement": crop_water_requirement,
        "cultivated_area": cultivated_area,
        "rainfall": rainfall,
        "irrigation_requirement": irrigation_requirement
    }


def compare_water_requirements(crop_data):
    """
    Compare water requirements of different crops.

    Each item should contain:
    crop
    crop_water_requirement
    cultivated_area
    rainfall
    """

    results = []

    for crop in crop_data:

        result = estimate_water_demand(
            crop=crop["crop"],
            crop_water_requirement=crop["crop_water_requirement"],
            cultivated_area=crop["cultivated_area"],
            rainfall=crop["rainfall"]
        )

        results.append(result)

    # Lowest irrigation requirement first
    results.sort(
        key=lambda item: item["irrigation_requirement"]
    )

    return results


if __name__ == "__main__":

    # Example test
    result = estimate_water_demand(
        crop="Rice",
        crop_water_requirement=1200,
        cultivated_area=1,
        rainfall=500
    )

    print("Crop:", result["crop"])
    print(
        "Irrigation Requirement:",
        result["irrigation_requirement"]
    )