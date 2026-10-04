def generate_recommendation(ranked_crops):
    """
    Generate the final crop recommendation
    from ranked crop results.
    """

    if not ranked_crops:
        return {
            "recommended_crop": None,
            "message": "No suitable crop found."
        }

    best_crop = ranked_crops[0]

    return {
        "recommended_crop": best_crop["crop"],
        "score": best_crop["score"],
        "message": (
            f"{best_crop['crop']} is the recommended crop "
            f"based on the overall sustainability score."
        )
    }


def get_top_recommendations(ranked_crops, top_n=3):
    """
    Return the top N recommended crops.
    """

    if not ranked_crops:
        return []

    return ranked_crops[:top_n]


def display_recommendation(ranked_crops):
    """
    Display the recommendation in a readable format.
    """

    recommendation = generate_recommendation(
        ranked_crops
    )

    print("Crop Recommendation")
    print("--------------------")

    if recommendation["recommended_crop"] is None:
        print(recommendation["message"])
        return

    print(
        "Recommended Crop:",
        recommendation["recommended_crop"]
    )

    print(
        "Overall Score:",
        recommendation["score"]
    )

    print(
        "Reason:",
        recommendation["message"]
    )


if __name__ == "__main__":

    # Example test data
    ranked_crops = [
        {
            "crop": "Maize",
            "score": 0.78
        },
        {
            "crop": "Rice",
            "score": 0.65
        },
        {
            "crop": "Groundnut",
            "score": 0.61
        }
    ]

    display_recommendation(ranked_crops)

    print("\nTop 3 Crops:")

    top_crops = get_top_recommendations(
        ranked_crops,
        top_n=3
    )

    for crop in top_crops:
        print(
            crop["crop"],
            "->",
            crop["score"]
        )