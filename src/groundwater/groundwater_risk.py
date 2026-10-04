def calculate_groundwater_risk(
    water_demand,
    groundwater_level,
    recharge_rate,
    cultivated_area
):
    """
    Calculate a groundwater sustainability risk score.

    water_demand: total crop water demand
    groundwater_level: groundwater level
    recharge_rate: groundwater recharge rate
    cultivated_area: cultivated area
    """

    if groundwater_level <= 0:
        raise ValueError("Groundwater level must be greater than 0.")

    if recharge_rate < 0:
        raise ValueError("Recharge rate cannot be negative.")

    if cultivated_area <= 0:
        raise ValueError("Cultivated area must be greater than 0.")

    # Water demand per unit cultivated area
    demand_per_area = water_demand / cultivated_area

    # Compare demand with available recharge
    recharge_ratio = demand_per_area / (recharge_rate + 1)

    # Groundwater level factor
    level_factor = 1 / groundwater_level

    # Combined risk score
    risk_score = (
        0.6 * recharge_ratio +
        0.4 * level_factor
    )

    return risk_score


def classify_groundwater_risk(risk_score):
    """
    Convert the numerical risk score into a risk category.
    """

    if risk_score < 0.5:
        return "Low"

    elif risk_score < 1.0:
        return "Medium"

    else:
        return "High"


def assess_groundwater(
    water_demand,
    groundwater_level,
    recharge_rate,
    cultivated_area
):
    """
    Complete groundwater risk assessment.
    """

    risk_score = calculate_groundwater_risk(
        water_demand,
        groundwater_level,
        recharge_rate,
        cultivated_area
    )

    risk_category = classify_groundwater_risk(
        risk_score
    )

    return {
        "water_demand": water_demand,
        "groundwater_level": groundwater_level,
        "recharge_rate": recharge_rate,
        "cultivated_area": cultivated_area,
        "risk_score": round(risk_score, 4),
        "risk_category": risk_category
    }


if __name__ == "__main__":

    # Example test data
    result = assess_groundwater(
        water_demand=1000,
        groundwater_level=10,
        recharge_rate=800,
        cultivated_area=1
    )

    print("Groundwater Risk Assessment")
    print("----------------------------")
    print("Risk Score:", result["risk_score"])
    print("Risk Category:", result["risk_category"])