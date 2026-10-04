def calculate_crop_score(
    yield_score,
    profit_score,
    water_score,
    groundwater_score
):
    """
    Calculate an overall sustainability score for a crop.

    Higher yield and profit are better.
    Lower water requirement and groundwater risk are better.
    """

    score = (
        0.30 * yield_score
        + 0.30 * profit_score
        + 0.20 * water_score
        + 0.20 * groundwater_score
    )

    return score


def rank_crops(crop_data):
    """
    Rank crops according to their overall score.

    Each crop should contain:
    crop
    yield_score
    profit_score
    water_score
    groundwater_score
    """

    results = []

    for crop in crop_data:

        score = calculate_crop_score(
            yield_score=crop["yield_score"],
            profit_score=crop["profit_score"],
            water_score=crop["water_score"],
            groundwater_score=crop["groundwater_score"]
        )

        results.append({
            "crop": crop["crop"],
            "score": round(score, 4)
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


def select_best_crop(crop_data):
    """
    Select the crop with the highest overall score.
    """

    ranked_crops = rank_crops(crop_data)

    if not ranked_crops:
        return None

    return ranked_crops[0]


if __name__ == "__main__":

    # Example data for testing
    crops = [
        {
            "crop": "Rice",
            "yield_score": 0.85,
            "profit_score": 0.70,
            "water_score": 0.40,
            "groundwater_score": 0.35
        },
        {
            "crop": "Maize",
            "yield_score": 0.75,
            "profit_score": 0.80,
            "water_score": 0.70,
            "groundwater_score": 0.75
        }
    ]

    ranked = rank_crops(crops)

    print("Crop Ranking")
    print("------------")

    for crop in ranked:
        print(
            crop["crop"],
            "->",
            crop["score"]
        )

    best_crop = select_best_crop(crops)

    print("\nRecommended Crop:", best_crop["crop"])