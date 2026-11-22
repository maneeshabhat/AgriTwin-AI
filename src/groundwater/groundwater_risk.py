
def calculate_groundwater_risk(
    water_demand,
    groundwater_level,
    recharge_rate,
    cultivated_area
):
    """
    Calculate seasonal groundwater recharge pressure.

    water_demand: seasonal irrigation demand (m3)
    groundwater_level: groundwater depth (metres)
    recharge_rate: annual recharge (m3/year)
    cultivated_area: area (hectares)
    """

    if water_demand < 0:
        raise ValueError("Water demand cannot be negative.")

    if groundwater_level <= 0:
        raise ValueError("Groundwater depth must be greater than zero.")

    if recharge_rate <= 0:
        raise ValueError("Annual recharge must be greater than zero.")

    if cultivated_area <= 0:
        raise ValueError("Cultivated area must be greater than zero.")

    # Seasonal demand compared with annual recharge
    recharge_pressure = water_demand / recharge_rate

    return recharge_pressure


def classify_groundwater_risk(risk_score):

    # Provisional academic prototype thresholds
    if risk_score <= 0.25:
        return "Low"

    elif risk_score <= 0.50:
        return "Moderate"

    else:
        return "High"


def assess_groundwater(
    water_demand,
    groundwater_level,
    recharge_rate,
    cultivated_area
):

    risk_score = calculate_groundwater_risk(
        water_demand,
        groundwater_level,
        recharge_rate,
        cultivated_area
    )

    return {
        "seasonal_water_demand_m3": round(water_demand, 2),
        "groundwater_depth_m": groundwater_level,
        "annual_recharge_m3": recharge_rate,
        "cultivated_area_hectares": cultivated_area,
        "recharge_pressure_ratio": round(risk_score, 4),
        "risk_category": classify_groundwater_risk(risk_score)
    }


if __name__ == "__main__":

    result = assess_groundwater(
        water_demand=7000,
        groundwater_level=10,
        recharge_rate=20000,
        cultivated_area=1
    )

    print("Groundwater Assessment")
    print("----------------------")
    print("Seasonal Demand:",
          result["seasonal_water_demand_m3"], "m3")
    print("Annual Recharge:",
          result["annual_recharge_m3"], "m3/year")
    print("Recharge Pressure:",
          result["recharge_pressure_ratio"])
    print("Risk Category:",
          result["risk_category"])
