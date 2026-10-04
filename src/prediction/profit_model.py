def calculate_profit(predicted_yield, market_price, farming_cost):
    """
    Calculate estimated profit.

    predicted_yield: expected crop yield
    market_price: price per unit of crop
    farming_cost: total farming cost
    """

    revenue = predicted_yield * market_price
    profit = revenue - farming_cost

    return profit


def predict_profit(predicted_yield, market_price, farming_cost):
    """
    Calculate revenue and profit for a crop.
    """

    revenue = predicted_yield * market_price
    profit = revenue - farming_cost

    return {
        "revenue": revenue,
        "profit": profit
    }


def compare_crops(crop_data):
    """
    Compare the estimated profit of multiple crops.

    crop_data should contain:
    crop
    predicted_yield
    market_price
    farming_cost
    """

    results = []

    for crop in crop_data:
        predicted_yield = crop["predicted_yield"]
        market_price = crop["market_price"]
        farming_cost = crop["farming_cost"]

        revenue = predicted_yield * market_price
        profit = revenue - farming_cost

        results.append({
            "crop": crop["crop"],
            "revenue": revenue,
            "profit": profit
        })

    results.sort(
        key=lambda item: item["profit"],
        reverse=True
    )

    return results


if __name__ == "__main__":
    # Example test data
    result = predict_profit(
        predicted_yield=2000,
        market_price=25,
        farming_cost=30000
    )

    print("Estimated Revenue:", result["revenue"])
    print("Estimated Profit:", result["profit"])