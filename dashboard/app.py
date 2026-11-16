
import streamlit as st
import pandas as pd
import joblib

@st.cache_resource
def load_yield_model():
    return joblib.load("models/yield_model.joblib")
# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgriTwin AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    h1 {
        color: #176b3a;
    }

    h2, h3 {
        color: #26734d;
    }

    .stButton > button {
        background-color: #218c50;
        color: white;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #176b3a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------

st.title("🌱 AgriTwin AI")

st.subheader(
    "Groundwater-Aware Intelligent Crop Recommendation "
    "and Sustainability Optimization System"
)

st.write(
    "Make smarter farming decisions with crop recommendations, "
    "yield estimation, water management and groundwater awareness."
)

st.divider()

# --------------------------------------------------
# 4. SIDEBAR
# --------------------------------------------------

st.sidebar.title("🌾 AgriTwin AI")

st.sidebar.write(
    "Smart and sustainable farming"
)

st.sidebar.info(
    "Enter your farm details to explore suitable crops "
    "and understand their resource requirements."
)

st.sidebar.caption(
    "Academic Project Prototype | MCA"
)

# --------------------------------------------------
# 5. FARM DETAILS
# --------------------------------------------------

st.header("1. Farm Details")

col1, col2 = st.columns(2)

with col1:

    farmer_name = st.text_input(
        "Farmer Name (Optional)"
    )

    region = st.selectbox(
    "Region",
    ["South", "North", "East", "West", "Central"]
)

    farm_area = st.number_input(
        "Cultivated Land Area (acres)",
        min_value=0.1,
        value=1.0,
        step=0.1
    )

with col2:

    season_options = {
    "Rainy Season (ಮಳೆಗಾಲ)": "Kharif",
    "Winter Season (ಚಳಿಗಾಲ)": "Rabi",
    "Summer Season (ಬೇಸಿಗೆ)": "Zaid"
}

    selected_season = st.selectbox(
        "Select Crop Growing Season",
        list(season_options.keys())
    )

    season = season_options[selected_season]

    soil_type = st.selectbox(
    "Soil Type",
    ["Clay", "Sandy", "Silt", "Loamy"]
)

    irrigation_type = st.selectbox(
    "Irrigation Type",
    ["Canal", "Rainfed", "Sprinkler", "Drip"]
)

st.divider()

# --------------------------------------------------
# 6. SOIL DETAILS
# --------------------------------------------------

st.header("2. Soil Details")

st.write(
    "Enter the available soil information. "
    "You can refer to your soil test report."
)

col1, col2, col3 = st.columns(3)

with col1:

    nitrogen = st.number_input(
        "Nitrogen (N)",
        min_value=0.0,
        value=80.0
    )

with col2:

    phosphorus = st.number_input(
        "Phosphorus (P)",
        min_value=0.0,
        value=40.0
    )

with col3:

    potassium = st.number_input(
        "Potassium (K)",
        min_value=0.0,
        value=40.0
    )

col1, col2 = st.columns(2)

with col1:

    soil_ph = st.number_input(
        "Soil pH",
        min_value=0.0,
        max_value=14.0,
        value=6.5
    )

with col2:

    soil_moisture = st.number_input(
        "Soil Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=45.0
    )

st.divider()

# --------------------------------------------------
# 7. WEATHER DETAILS
# --------------------------------------------------

st.header("3. Weather Details")

st.write(
    "Enter the weather information for your farming area."
)

col1, col2, col3 = st.columns(3)

with col1:

    temperature = st.number_input(
        "Temperature (°C)",
        value=28.0
    )

with col2:

    humidity = st.number_input(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=75.0
    )

with col3:

    rainfall = st.number_input(
        "Rainfall (mm)",
        min_value=0.0,
        value=100.0
    )

st.divider()

# --------------------------------------------------
# 8. GROUNDWATER DETAILS
# --------------------------------------------------

st.header("4. Groundwater Details")

st.write(
    "Enter groundwater information from your borewell "
    "or available local groundwater records."
)

col1, col2 = st.columns(2)

with col1:

    groundwater_level = st.number_input(
        "Groundwater Depth (metres)",
        min_value=0.1,
        value=10.0
    )

with col2:

    recharge_rate = st.number_input(
        "Groundwater Recharge Rate",
        min_value=0.0,
        value=5.0
    )

st.caption(
    "Use consistent units for groundwater recharge and water demand. "
    "These values are currently prototype inputs."
)

st.divider()

# --------------------------------------------------
# 9. GENERATE FARM SUMMARY
# --------------------------------------------------

st.header("5. Generate Crop Recommendation")

if st.button(
    "🌾 Generate Crop Recommendation",
    type="primary"
):

    # Collect all farmer inputs

    farm_data = {
        "Farmer Name": farmer_name if farmer_name else "Not provided",
        "Village / District": region,
        "Cultivated Area (acres)": farm_area,
        "Growing Season": selected_season,
        "Season Code": season,
        "Soil Type": soil_type,
        "Watering Method": irrigation_type,
        "Nitrogen (N)": nitrogen,
        "Phosphorus (P)": phosphorus,
        "Potassium (K)": potassium,
        "Soil pH": soil_ph,
        "Soil Moisture (%)": soil_moisture,
        "Temperature (°C)": temperature,
        "Humidity (%)": humidity,
        "Rainfall (mm)": rainfall,
        "Groundwater Depth (m)": groundwater_level,
        "Groundwater Recharge Rate": recharge_rate
    }

    st.success(
        "Farm details submitted successfully!"
    )

    st.subheader("Your Farm Details")

    summary_df = pd.DataFrame(
        list(farm_data.items()),
        columns=["Parameter", "Entered Value"]
    )

    # Fix PyArrow mixed-data-type error

    summary_df["Entered Value"] = (
        summary_df["Entered Value"].astype(str)
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

       # ------------------------------------------
    # CROP YIELD PREDICTION
    # ------------------------------------------

    st.subheader("🌾 Crop Yield Predictions")

    try:
        model = load_yield_model()

        # Dataset-based default values for
        # fields not collected in the dashboard.

        default_features = {
            "Organic_Carbon": 0.96,
            "Sunlight_Hours": 7.51,
            "Wind_Speed": 9.50,
            "Altitude": 1103.36,
            "Fertilizer_Used": 205.99,
            "Pesticide_Used": 12.53
        }

        crop_list = [
            "Maize",
            "Potato",
            "Rice",
            "Sugarcane",
            "Wheat",
            "Cotton"
        ]

        predictions = []

        # Convert cultivated area from acres to hectares.
        area_hectares = farm_area * 0.404686

        for crop in crop_list:

            input_data = {
                "N": nitrogen,
                "P": phosphorus,
                "K": potassium,
                "Soil_pH": soil_ph,
                "Soil_Moisture": soil_moisture,
                "Soil_Type": soil_type,
                "Organic_Carbon": default_features["Organic_Carbon"],
                "Temperature": temperature,
                "Humidity": humidity,
                "Rainfall": rainfall,
                "Sunlight_Hours": default_features["Sunlight_Hours"],
                "Wind_Speed": default_features["Wind_Speed"],
                "Region": region,
                "Altitude": default_features["Altitude"],
                "Season": season,
                "Crop_Type": crop,
                "Irrigation_Type": irrigation_type,
                "Fertilizer_Used": default_features["Fertilizer_Used"],
                "Pesticide_Used": default_features["Pesticide_Used"]
            }

            predicted_yield = float(model.predict(
                pd.DataFrame([input_data])
            )[0])

            total_yield = predicted_yield * area_hectares

            predictions.append({
                "Crop": crop,
                "Predicted Yield (tonnes/hectare)": round(
                    predicted_yield, 2
                ),
                "Estimated Total Yield (tonnes)": round(
                    total_yield, 2
                )
            })

        # Sort crops by predicted yield.
        predictions.sort(
            key=lambda x: x["Predicted Yield (tonnes/hectare)"],
            reverse=True
        )

        prediction_df = pd.DataFrame(predictions)

        st.success("Crop yield predictions generated successfully!")

        st.dataframe(
            prediction_df,
            use_container_width=True,
            hide_index=True
        )

        best_crop = predictions[0]

        st.subheader("🏆 Highest Predicted Yield")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Suggested Crop",
                best_crop["Crop"]
            )

        with col2:
            st.metric(
                "Predicted Yield",
                str(best_crop["Predicted Yield (tonnes/hectare)"])
                + " tonnes/hectare"
            )

    except Exception as e:
        st.error(f"Prediction error: {e}")

    st.caption(
        "Note: Predictions are based on the trained academic "
        "dataset and average values for fields not entered by "
        "the farmer. They are experimental estimates, not "
        "validated agricultural advice."
    )
    # Download farm input summary

    csv_data = summary_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Farm Details",
        data=csv_data,
        file_name="agritwin_farm_details.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# 10. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AgriTwin AI | Groundwater-Aware Smart Agriculture | "
    "Academic Project Prototype"
)

# --------------------------------------------------
# 9. CROP MARKET PRICE AND CULTIVATION COST
# --------------------------------------------------

st.header("5. Crop Market Prices and Farming Costs")

st.write(
    "Enter the estimated selling price and cultivation "
    "cost for each crop. Use your local market prices."
)

crop_financial_data = pd.DataFrame({
    "Crop": [
        "Maize", "Potato", "Rice",
        "Sugarcane", "Wheat", "Cotton"
    ],
    "Market Price (₹/tonne)": [0, 0, 0, 0, 0, 0],
    "Cultivation Cost (₹/acre)": [0, 0, 0, 0, 0, 0]
})

edited_financial_data = st.data_editor(
    crop_financial_data,
    use_container_width=True,
    hide_index=True,
    disabled=["Crop"],
    column_config={
        "Market Price (₹/tonne)": st.column_config.NumberColumn(
            min_value=0,
            step=100
        ),
        "Cultivation Cost (₹/acre)": st.column_config.NumberColumn(
            min_value=0,
            step=500
        )
    },
    key="crop_financial_data"
)

st.caption(
    "Enter prices in rupees per tonne and cultivation "
    "costs in rupees per acre. These are farmer-provided estimates."
)

st.divider()
