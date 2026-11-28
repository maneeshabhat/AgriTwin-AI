import os
import sys
import sqlite3
import hashlib
import hmac

import joblib
import pandas as pd
import streamlit as st

# ============================================================
# AGRITWIN AI - COMPLETE STREAMLIT APPLICATION
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.prediction.water_model import compare_water_requirements
from src.groundwater.groundwater_risk import assess_groundwater
from src.optimization.optimizer import rank_crops
from src.recommendation.recommender import (
    generate_recommendation,
    get_top_recommendations
)

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "yield_model.joblib")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "agritwin_farmers.db")

CROPS = ["Maize", "Potato","Rice", "Sugarcane", "Wheat", "Cotton"]
# Broad seasonal shortlist for the academic prototype.
# Sugarcane is a long-duration crop, so local planting conditions matter.
SEASON_CROP_SUITABILITY = {
    "Kharif": ["Maize", "Rice", "Cotton", "Sugarcane"],
    "Rabi": ["Potato", "Wheat", "Maize", "Rice", "Sugarcane"],
    "Zaid": ["Maize", "Rice", "Sugarcane"]
}
st.set_page_config(
    page_title="AgriTwin AI | Smart Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# MODEL
# ============================================================

@st.cache_resource
def load_yield_model():
    return joblib.load(MODEL_PATH)


# ============================================================
# DATABASE AND AUTHENTICATION
# ============================================================

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def create_farmer_table():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200000
    )
    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        candidate = hash_password(
            password,
            bytes.fromhex(salt_hex)
        ).split(":")[1]

        return hmac.compare_digest(candidate, hash_hex)

    except (ValueError, TypeError):
        return False


create_farmer_table()


if "farmer_logged_in" not in st.session_state:
    st.session_state["farmer_logged_in"] = False

if "farmer_name" not in st.session_state:
    st.session_state["farmer_name"] = ""


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f4f8f2;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#123d2b 0%,#1d593b 100%);
}

[data-testid="stSidebar"] * {
    color: #f4fff6 !important;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: #163d2c;
}

.hero {
    padding: 34px 36px;
    border-radius: 22px;
    color: white;
    background: linear-gradient(
        90deg,
        rgba(10,42,27,.92),
        rgba(15,75,43,.58)
    ),
    url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85');
    background-size: cover;
    background-position: center;
    margin-bottom: 22px;
}

.hero h1 {
    color: white !important;
    font-size: 2.55rem;
}

.hero p {
    color: #e9f5e9;
    font-size: 1.04rem;
}

.eyebrow {
    color: #b8e6c2;
    font-weight: 700;
    letter-spacing: 2px;
    font-size: .76rem;
}

.info-card {
    background: white;
    border: 1px solid #e2ecdf;
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 115px;
}

.info-card .label {
    color: #64806c;
    font-size: .83rem;
    font-weight: 600;
}

.info-card .value {
    color: #173e2c;
    font-family: 'Manrope';
    font-size: 1.65rem;
    font-weight: 800;
    margin-top: 5px;
}

.feature-card {
    background: white;
    border: 1px solid #e2ecdf;
    border-radius: 16px;
    padding: 20px;
    min-height: 150px;
}

.feature-card h3 {
    font-size: 1.05rem;
}

.feature-card p {
    color: #687c6e;
    font-size: .88rem;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#1d7547,#2c965b);
    border: 0;
    border-radius: 11px;
    min-height: 45px;
    font-weight: 700;
    color: white;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2ecdf;
    padding: 14px 16px;
    border-radius: 14px;
}

hr {
    border-color: #e0eadd;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# COMMON DISPLAY FUNCTIONS
# ============================================================

def hero(title, subtitle, eyebrow="AGRI INTELLIGENCE"):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_card(label, value, hint=""):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div>{hint}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def feature(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div style="font-size:1.8rem">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def normalize_scores(values, lower_is_better=False):
    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [1.0] * len(values)

    if lower_is_better:
        return [
            round((maximum - value) / (maximum - minimum), 4)
            for value in values
        ]

    return [
        round((value - minimum) / (maximum - minimum), 4)
        for value in values
    ]


# ============================================================
# LOGIN / REGISTRATION
# ============================================================

if not st.session_state["farmer_logged_in"]:

    st.markdown("""
    <div style="max-width:760px;margin:3rem auto 1rem;padding:2rem;
    background:white;border:1px solid #e2ecdf;border-radius:22px;">
        <div style="font-size:2.6rem;">🌱</div>
        <div style="font-weight:800;color:#4c805f;">
            SMART • SUSTAINABLE • DATA-DRIVEN
        </div>
        <h1>Welcome to AgriTwin AI</h1>
        <p>Sign in or create a farmer account to analyse your farm.</p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(
        ["Farmer Login", "Create Account"]
    )

    with login_tab:

        with st.form("farmer_login_form"):

            login_username = st.text_input("Username")
            login_password = st.text_input(
                "Password",
                type="password"
            )

            login_submit = st.form_submit_button(
                "Login",
                type="primary",
                use_container_width=True
            )

        if login_submit:

            username = login_username.strip().lower()

            with get_db_connection() as conn:
                record = conn.execute(
                    """
                    SELECT full_name, password_hash
                    FROM farmers
                    WHERE username = ?
                    """,
                    (username,)
                ).fetchone()

            if record and verify_password(login_password, record[1]):

                st.session_state["farmer_logged_in"] = True
                st.session_state["farmer_name"] = record[0]
                st.session_state["farmer_username"] = username

                st.rerun()

            else:
                st.error("Incorrect username or password.")

    with register_tab:

        if "register_form_version" not in st.session_state:
            st.session_state["register_form_version"] = 0

        version = st.session_state["register_form_version"]

        with st.form(f"register_form_{version}"):

            full_name = st.text_input("Farmer's full name")
            new_username = st.text_input("Choose a username")

            new_password = st.text_input(
                "Create password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            register_submit = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True
            )

        if register_submit:

            clean_name = full_name.strip()
            clean_username = new_username.strip().lower()

            if not clean_name or not clean_username or not new_password:
                st.error("Please fill in all fields.")

            elif len(clean_username) < 4:
                st.error("Username must contain at least 4 characters.")

            elif len(new_password) < 8:
                st.error("Password must contain at least 8 characters.")

            elif new_password != confirm_password:
                st.error("Passwords do not match.")

            else:

                try:
                    with get_db_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO farmers
                            (full_name, username, password_hash)
                            VALUES (?, ?, ?)
                            """,
                            (
                                clean_name,
                                clean_username,
                                hash_password(new_password)
                            )
                        )

                    st.success("Account created. Please log in.")

                    st.session_state["register_form_version"] += 1
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error("That username is already taken.")

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🌱 AgriTwin AI")
    st.caption("SMART • SUSTAINABLE • DATA-DRIVEN")
    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "🏡 Overview",
            "🧑‍🌾 Farm Analysis",
            "📊 Insights & Results"
        ],
        key="navigation_radio"
    )

    st.markdown("---")
    st.caption(f"Logged in as: {st.session_state['farmer_name']}")

    if st.button(
        "Logout",
        key="farmer_logout",
        type="primary",
        use_container_width=True
    ):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()

    st.markdown("---")
    st.markdown("**Your agriculture companion**")
    st.caption("Groundwater-aware crop planning")
    st.caption("Academic project prototype")


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏡 Overview":

    hero(
        "Grow smarter. Farm sustainably.",
        "An intelligent crop-planning workspace combining yield prediction, "
        "farm economics, irrigation demand and groundwater awareness.",
        "GROUNDWATER-AWARE SMART FARMING"
    )

    st.markdown("### Your farm, viewed through data")

    st.write(
        "Enter your field conditions in Farm Analysis to generate "
        "crop-wise estimates and recommendations."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        info_card("CROP OPTIONS", "06", "Six crops")

    with c2:
        info_card("MODEL INPUTS", "19", "Features in trained pipeline")

    with c3:
        info_card("DATASET", "10,000", "Crop-yield records")

    with c4:
        info_card("CORE FOCUS", "Water", "Yield + profit + sustainability")

    st.markdown("### Explore the platform")

    a, b, c = st.columns(3)

    with a:
        feature(
            "🌾",
            "Yield intelligence",
            "Estimate crop yield using the trained Random Forest pipeline."
        )

    with b:
        feature(
            "💧",
            "Water planning",
            "Estimate seasonal irrigation requirements."
        )

    with c:
        feature(
            "🌍",
            "Groundwater awareness",
            "View recharge-pressure indicators."
        )

    st.markdown("---")

    st.info(
        "Start with Farm Analysis in the left navigation. "
        "After generating results, open Insights & Results."
    )


# ============================================================
# FARM ANALYSIS
# ============================================================

elif page == "🧑‍🌾 Farm Analysis":

    hero(
        "Tell us about your farm",
        "Complete all four steps to generate your crop recommendations.",
        "FARM INPUT WORKSPACE"
    )

    st.info(
        "Enter actual farm information wherever possible. "
        "Rainfall may be zero if that is the genuine measured value."
    )

    # --------------------------------------------------------
    # DURABLE FORM DATA
    # --------------------------------------------------------

    if "farm_form_data" not in st.session_state:
        st.session_state["farm_form_data"] = {}

    saved = st.session_state["farm_form_data"]

    defaults = {
        "farmer_name_input": st.session_state["farmer_name"],
        "region_input": "South",
        "farm_area_input": 0.0,
        "season_input": "Rainy Season (Kharif)",
        "soil_type_input": "Loamy",
        "irrigation_input": "Rainfed",
        "temperature_input": 0.0,
        "humidity_input": 0.0,
        "rainfall_input": 0.0,
        "groundwater_level_input": 0.0,
        "recharge_rate_input": 0.0
    }

    step1_keys = [
        "farmer_name_input",
        "region_input",
        "farm_area_input",
        "season_input",
        "soil_type_input",
        "irrigation_input"
    ]

    step2_keys = [
        "temperature_input",
        "humidity_input",
        "rainfall_input"
    ]

    step3_keys = [
        "groundwater_level_input",
        "recharge_rate_input"
    ]

    if "farm_step" not in st.session_state:
        st.session_state["farm_step"] = 1

    step = st.session_state["farm_step"]

    # Restore only the current step's values.
    # Do not overwrite values while the current widgets are active.

    keys_by_step = {
        1: step1_keys,
        2: step2_keys,
        3: step3_keys
    }

    for key in keys_by_step.get(step, []):

        if key not in st.session_state:
            st.session_state[key] = saved.get(
                key,
                defaults[key]
            )

    def save_values(keys, values):
        for key in keys:
            st.session_state["farm_form_data"][key] = values[key]

    st.progress(step / 4, text=f"Step {step} of 4")


    # ========================================================
    # STEP 1 - FARM AND SOIL
    # ========================================================

    if step == 1:

        st.subheader("1. Farm & Soil Details")

        with st.form("farm_step_1"):

            farmer_name = st.text_input(
                "Farmer name",
                key="farmer_name_input"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                region = st.selectbox(
                    "Region",
                    ["South", "North", "East", "West", "Central"],
                    key="region_input"
                )

                farm_area = st.number_input(
                    "Cultivated area (acres)",
                    min_value=0.0,
                    step=0.1,
                    key="farm_area_input"
                )

            with c2:

                season_label = st.selectbox(
                    "Growing season",
                    [
                        "Rainy Season (Kharif)",
                        "Winter Season (Rabi)",
                        "Summer Season (Zaid)"
                    ],
                    key="season_input"
                )

                soil_type = st.selectbox(
                    "Soil type",
                    ["Clay", "Sandy", "Silt", "Loamy"],
                    key="soil_type_input"
                )

            with c3:

                irrigation_type = st.selectbox(
                    "Irrigation type",
                    ["Canal", "Rainfed", "Sprinkler", "Drip"],
                    key="irrigation_input"
                )

            next1 = st.form_submit_button(
                "Next: Weather →",
                type="primary",
                use_container_width=True
            )

        if next1:

            values = {
                "farmer_name_input": farmer_name,
                "region_input": region,
                "farm_area_input": farm_area,
                "season_input": season_label,
                "soil_type_input": soil_type,
                "irrigation_input": irrigation_type
            }

            save_values(step1_keys, values)

            missing = []

            if not farmer_name.strip():
                missing.append("Farmer name")

            if farm_area <= 0:
                missing.append("Cultivated area")

            if missing:
                st.error("Please complete: " + "; ".join(missing))

            else:

                st.session_state["farmer_name"] = farmer_name.strip()
                st.session_state["region"] = region
                st.session_state["farm_area"] = farm_area
                st.session_state["season_label"] = season_label
                st.session_state["soil_type"] = soil_type
                st.session_state["irrigation_type"] = irrigation_type

                st.session_state["farm_step"] = 2
                st.rerun()


    # ========================================================
    # STEP 2 - WEATHER
    # ========================================================

    elif step == 2:

        st.subheader("2. Weather Details")

        with st.form("farm_step_2"):

            c1, c2, c3 = st.columns(3)

            with c1:

                temperature = st.number_input(
                    "Temperature (°C)",
                    min_value=-10.0,
                    max_value=60.0,
                    step=0.5,
                    key="temperature_input"
                )

            with c2:

                humidity = st.number_input(
                    "Humidity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    key="humidity_input"
                )

            with c3:

                rainfall = st.number_input(
                    "Seasonal rainfall (mm)",
                    min_value=0.0,
                    step=10.0,
                    key="rainfall_input"
                )

            st.caption(
                "Enter rainfall as zero only if no rainfall was recorded."
            )

            b1, b2 = st.columns(2)

            back2 = b1.form_submit_button(
                "← Back",
                use_container_width=True
            )

            next2 = b2.form_submit_button(
                "Next: Groundwater →",
                type="primary",
                use_container_width=True
            )

        if back2:

            values = {
                "temperature_input": temperature,
                "humidity_input": humidity,
                "rainfall_input": rainfall
            }

            save_values(step2_keys, values)

            st.session_state["farm_step"] = 1
            st.rerun()

        if next2:

            # Validate the values returned by the widgets.
            # Do not read potentially stale values from session state.

            if temperature <= 0:

                st.error("Temperature must be greater than zero.")

            elif humidity <= 0:

                st.error("Humidity must be greater than zero.")

            else:

                values = {
                    "temperature_input": temperature,
                    "humidity_input": humidity,
                    "rainfall_input": rainfall
                }

                save_values(step2_keys, values)

                st.session_state["temperature"] = temperature
                st.session_state["humidity"] = humidity
                st.session_state["rainfall"] = rainfall

                st.session_state["farm_step"] = 3
                st.rerun()


    # ========================================================
    # STEP 3 - GROUNDWATER
    # ========================================================

    elif step == 3:

        st.subheader("3. Groundwater Details")

        with st.form("farm_step_3"):

            c1, c2 = st.columns(2)

            with c1:

                groundwater_level = st.number_input(
                    "Groundwater depth (metres)",
                    min_value=0.0,
                    step=0.5,
                    key="groundwater_level_input"
                )

            with c2:

                recharge_rate = st.number_input(
                    "Annual groundwater recharge (m³/year)",
                    min_value=0.0,
                    step=100.0,
                    key="recharge_rate_input"
                )

            st.warning(
                "Use locally sourced recharge information. "
                "The current groundwater ratio is a simplified "
                "prototype indicator."
            )

            b1, b2 = st.columns(2)

            back3 = b1.form_submit_button(
                "← Back",
                use_container_width=True
            )

            next3 = b2.form_submit_button(
                "Next: Costs & Water →",
                type="primary",
                use_container_width=True
            )

        if back3:

            values = {
                "groundwater_level_input": groundwater_level,
                "recharge_rate_input": recharge_rate
            }

            save_values(step3_keys, values)

            st.session_state["farm_step"] = 2
            st.rerun()

        if next3:

            if groundwater_level <= 0:

                st.error("Groundwater depth must be greater than zero.")

            elif recharge_rate <= 0:

                st.error("Annual recharge must be greater than zero.")

            else:

                values = {
                    "groundwater_level_input": groundwater_level,
                    "recharge_rate_input": recharge_rate
                }

                save_values(step3_keys, values)

                st.session_state["groundwater_level"] = groundwater_level
                st.session_state["recharge_rate"] = recharge_rate

                st.session_state["farm_step"] = 4
                st.rerun()


    # ========================================================
    # STEP 4 - COSTS AND WATER
    # ========================================================

    elif step == 4:

        st.subheader("4. Costs & Water Details")

        st.markdown("#### Crop-wise market price and cultivation cost")

        financial_default = pd.DataFrame({
            "Crop": CROPS,
            "Market Price (₹/tonne)": [0.0] * 6,
            "Cultivation Cost (₹/acre)": [0.0] * 6
        })

        financial_data = st.data_editor(
            saved.get("financial_editor", financial_default),
            use_container_width=True,
            hide_index=True,
            disabled=["Crop"],
            key=f"financial_editor_widget_{st.session_state.get('editor_version', 0)}",
            column_config={
                "Market Price (₹/tonne)": st.column_config.NumberColumn(
                    min_value=0.0,
                    step=100.0
                ),
                "Cultivation Cost (₹/acre)": st.column_config.NumberColumn(
                    min_value=0.0,
                    step=500.0
                )
            }
        )

        st.markdown("#### Seasonal crop water assumptions")

        water_default = pd.DataFrame({
            "Crop": CROPS,
            "Water Requirement (mm/season)": [0.0] * 6,
            "Effective Rainfall (mm/season)": [0.0] * 6
        })

        water_data = st.data_editor(
            saved.get("water_editor", water_default),
            use_container_width=True,
            hide_index=True,
            disabled=["Crop"],
            key=f"water_editor_widget_{st.session_state.get('editor_version', 0)}",
            column_config={
                "Water Requirement (mm/season)": st.column_config.NumberColumn(
                    min_value=0.0,
                    step=10.0
                ),
                "Effective Rainfall (mm/season)": st.column_config.NumberColumn(
                    min_value=0.0,
                    step=10.0
                )
            }
        )

        st.session_state["farm_form_data"]["financial_editor"] = (
            financial_data.copy()
        )

        st.session_state["farm_form_data"]["water_editor"] = (
            water_data.copy()
        )

        st.caption(
            "Enter prices, costs and water requirements for all crops. "
            "Effective rainfall may be zero."
        )

        b1, b2, b3 = st.columns(3)

        with b1:

            if st.button("← Back", use_container_width=True):

                st.session_state["farm_form_data"]["financial_editor"] = (
                    financial_data.copy()
                )

                st.session_state["farm_form_data"]["water_editor"] = (
                    water_data.copy()
                )

                st.session_state["farm_step"] = 3
                st.rerun()

        with b2:

            if st.button("Reset form", use_container_width=True):

                st.session_state["farm_form_data"] = {}

                st.session_state.pop("agritwin_results", None)

                for key in [
                    "temperature",
                    "humidity",
                    "rainfall",
                    "groundwater_level",
                    "recharge_rate",
                    "farmer_name",
                    "region",
                    "farm_area",
                    "season_label",
                    "soil_type",
                    "irrigation_type"
                ]:
                    st.session_state.pop(key, None)

                st.session_state["farm_step"] = 1

                # Change editor widget keys so old table values are not reused.
                st.session_state["editor_version"] = (
                    st.session_state.get("editor_version", 0) + 1
                )

                st.rerun()

        with b3:

            submitted = st.button(
                "🌾 Generate my farm analysis",
                use_container_width=True
            )

        if submitted:

            st.session_state["farm_form_data"]["financial_editor"] = (
                financial_data.copy()
            )

            st.session_state["farm_form_data"]["water_editor"] = (
                water_data.copy()
            )

            prices_ok = (
                financial_data["Market Price (₹/tonne)"] > 0
            ).all()

            costs_ok = (
                financial_data["Cultivation Cost (₹/acre)"] > 0
            ).all()

            water_ok = (
                water_data["Water Requirement (mm/season)"] > 0
            ).all()

            rain_ok = (
                water_data["Effective Rainfall (mm/season)"] >= 0
            ).all()

            if not prices_ok or not costs_ok or not water_ok or not rain_ok:

                st.error(
                    "Complete every crop row. Enter a market price, "
                    "cultivation cost and positive water requirement "
                    "for all six crops. Effective rainfall may be zero."
                )

            else:

                try:

                    farmer_name = st.session_state["farmer_name"]
                    region = st.session_state["region"]
                    farm_area = st.session_state["farm_area"]
                    season_label = st.session_state["season_label"]
                    soil_type = st.session_state["soil_type"]
                    irrigation_type = st.session_state["irrigation_type"]

                    season = {
                        "Rainy Season (Kharif)": "Kharif",
                        "Winter Season (Rabi)": "Rabi",
                        "Summer Season (Zaid)": "Zaid"
                    }[season_label]

                    temperature = st.session_state["temperature"]
                    humidity = st.session_state["humidity"]
                    rainfall = st.session_state["rainfall"]

                    groundwater_level = st.session_state["groundwater_level"]
                    recharge_rate = st.session_state["recharge_rate"]

                    # Baseline assumptions for model inputs not collected
                    # from the farmer.
                    nitrogen = 50.0
                    phosphorus = 40.0
                    potassium = 40.0
                    soil_ph = 6.5
                    soil_moisture = 30.0

                    model = load_yield_model()

                    area_hectares = farm_area * 0.404686

                    defaults_model = {
                        "Organic_Carbon": 0.96,
                        "Sunlight_Hours": 7.51,
                        "Wind_Speed": 9.50,
                        "Altitude": 1103.36,
                        "Fertilizer_Used": 205.99,
                        "Pesticide_Used": 12.53
                    }

                    # ------------------------------------------------
                    # YIELD PREDICTION
                    # ------------------------------------------------

                    predictions = []

                    for crop in CROPS:

                        row = {
                            "N": nitrogen,
                            "P": phosphorus,
                            "K": potassium,
                            "Soil_pH": soil_ph,
                            "Soil_Moisture": soil_moisture,
                            "Soil_Type": soil_type,
                            "Organic_Carbon": defaults_model["Organic_Carbon"],
                            "Temperature": temperature,
                            "Humidity": humidity,
                            "Rainfall": rainfall,
                            "Sunlight_Hours": defaults_model["Sunlight_Hours"],
                            "Wind_Speed": defaults_model["Wind_Speed"],
                            "Region": region,
                            "Altitude": defaults_model["Altitude"],
                            "Season": season,
                            "Crop_Type": crop,
                            "Irrigation_Type": irrigation_type,
                            "Fertilizer_Used": defaults_model["Fertilizer_Used"],
                            "Pesticide_Used": defaults_model["Pesticide_Used"]
                        }

                        predicted = float(
                            model.predict(pd.DataFrame([row]))[0]
                        )

                        predictions.append({
                            "Crop": crop,
                            "Predicted Yield (tonnes/hectare)": round(
                                predicted, 2
                            ),
                            "Estimated Total Yield (tonnes)": round(
                                predicted * area_hectares, 2
                            )
                        })

                    predictions.sort(
                        key=lambda x: x[
                            "Predicted Yield (tonnes/hectare)"
                        ],
                        reverse=True
                    )

                    # ------------------------------------------------
                    # PROFIT CALCULATION
                    # ------------------------------------------------

                    financial_results = []

                    for pred in predictions:

                        r = financial_data[
                            financial_data["Crop"] == pred["Crop"]
                        ].iloc[0]

                        price = float(r["Market Price (₹/tonne)"])
                        cost = float(r["Cultivation Cost (₹/acre)"])

                        revenue = (
                            pred["Estimated Total Yield (tonnes)"] * price
                        )

                        total_cost = cost * farm_area

                        financial_results.append({
                            "Crop": pred["Crop"],
                            "Estimated Yield (tonnes)": pred[
                                "Estimated Total Yield (tonnes)"
                            ],
                            "Revenue (₹)": round(revenue, 2),
                            "Cultivation Cost (₹)": round(total_cost, 2),
                            "Estimated Profit (₹)": round(
                                revenue - total_cost, 2
                            )
                        })

                    financial_results.sort(
                        key=lambda x: x["Estimated Profit (₹)"],
                        reverse=True
                    )

                    # ------------------------------------------------
                    # WATER REQUIREMENT
                    # ------------------------------------------------

                    water_inputs = []

                    for _, r in water_data.iterrows():

                        water_inputs.append({
                            "crop": r["Crop"],
                            "crop_water_requirement": float(
                                r["Water Requirement (mm/season)"]
                            ),
                            "cultivated_area": area_hectares,
                            "effective_rainfall": float(
                                r["Effective Rainfall (mm/season)"]
                            )
                        })

                    water_results = compare_water_requirements(
                        water_inputs
                    )

                    # ------------------------------------------------
                    # GROUNDWATER ASSESSMENT
                    # ------------------------------------------------

                    groundwater_results = []

                    for item in water_results:

                        assessment = assess_groundwater(
                            water_demand=item[
                                "irrigation_requirement_m3"
                            ],
                            groundwater_level=groundwater_level,
                            recharge_rate=recharge_rate,
                            cultivated_area=area_hectares
                        )

                        groundwater_results.append({
                            "Crop": item["crop"],
                            "Seasonal Irrigation Demand (m³)": assessment[
                                "seasonal_water_demand_m3"
                            ],
                            "Annual Recharge (m³/year)": assessment[
                                "annual_recharge_m3"
                            ],
                            "Recharge Pressure Ratio": assessment[
                                "recharge_pressure_ratio"
                            ],
                            "Risk Category": assessment["risk_category"]
                        })

                    # ------------------------------------------------
                    # SEASON-AWARE MULTI-OBJECTIVE CROP OPTIMIZATION
                    # ------------------------------------------------

                    # Select crops suitable for the selected season shortlist.
                    eligible_crops = SEASON_CROP_SUITABILITY.get(season, CROPS)

                    # Exclude other crops from the final seasonal recommendation.
                    candidate_predictions = [
                        item for item in predictions
                        if item["Crop"] in eligible_crops
                    ]

                    # Get the corresponding financial, water and groundwater values.
                    profit_map = {
                        item["Crop"]: item["Estimated Profit (₹)"]
                        for item in financial_results
                    }

                    water_map = {
                        item["crop"]: item["irrigation_requirement_m3"]
                        for item in water_results
                    }

                    groundwater_map = {
                        item["Crop"]: item["Recharge Pressure Ratio"]
                        for item in groundwater_results
                    }

                    candidate_names = [
                        item["Crop"] for item in candidate_predictions
                    ]

                    profit_values = [
                        profit_map[crop] for crop in candidate_names
                    ]

                    water_values = [
                        water_map[crop] for crop in candidate_names
                    ]

                    groundwater_values = [
                        groundwater_map[crop] for crop in candidate_names
                    ]

                    # Normalize each objective separately.
                    profit_scores = normalize_scores(profit_values)

                    water_scores = normalize_scores(
                        water_values,
                        lower_is_better=True
                    )

                    groundwater_scores = normalize_scores(
                        groundwater_values,
                        lower_is_better=True
                    )

                    # Weighted scoring:
                    # 55% estimated profit
                    # 30% irrigation efficiency
                    # 15% groundwater pressure
                    #
                    # Predicted raw yield is NOT directly included because
                    # tonnes/hectare are not directly comparable across crop types.

                    optimization_results = []

                    for i, crop in enumerate(candidate_names):

                        total_score = (
                            0.55 * profit_scores[i]
                            + 0.30 * water_scores[i]
                            + 0.15 * groundwater_scores[i]
                        )

                        optimization_results.append({
                            "Crop": crop,
                            "Overall Score (/100)": round(total_score * 100, 2),
                            "Profit Score": round(profit_scores[i] * 100, 2),
                            "Water Score": round(water_scores[i] * 100, 2),
                            "Groundwater Score": round(
                                groundwater_scores[i] * 100, 2
                            ),
                            "Estimated Profit (₹)": round(
                                profit_values[i], 2
                            ),
                            "Irrigation Demand (m³)": round(
                                water_values[i], 2
                            ),
                            "Recharge Pressure Ratio": round(
                                groundwater_values[i], 4
                            )
                        })

                    # Rank candidates by their overall score.
                    optimization_results.sort(
                        key=lambda x: x["Overall Score (/100)"],
                        reverse=True
                    )

                    # Select the best seasonal crop.
                    winner = optimization_results[0]

                    recommendation = (
                        f'{winner["Crop"]} '
                        f'(Overall suitability score: '
                        f'{winner["Overall Score (/100)"]}/100)'
                    )

                    recommendation_reason = (
                        f'{winner["Crop"]} ranked first for the selected {season} '
                        f'season shortlist based on the entered profit, irrigation '
                        f'demand and groundwater assumptions.'
                    )

                    # Prepare the top three recommendations for the dashboard.
                    top_recommendations = [
                        {
                            "Rank": i + 1,
                            **item
                        }
                        for i, item in enumerate(optimization_results[:3])
                        ]

                    # ------------------------------------------------
                    # SAVE RESULTS
                    # ------------------------------------------------

                    st.session_state["agritwin_results"] = {
                        "farmer_name": farmer_name,
                        "region": region,
                        "farm_area": farm_area,
                        "area_hectares": area_hectares,
                        "season": season_label,
                        "soil_type": soil_type,
                        "irrigation_type": irrigation_type,
                        "predictions": predictions,
                        "financial": financial_results,
                        "water": water_results,
                        "groundwater": groundwater_results,
                        "eligible_crops": eligible_crops,
                        "recommendation_reason": recommendation_reason,
                        "water_ready": True,
                        "farm_summary": {
                            "Farmer Name": farmer_name,
                            "Region": region,
                            "Cultivated Area (acres)": farm_area,
                            "Season": season_label,
                            "Soil Type": soil_type,
                            "Irrigation Type": irrigation_type,
                            "Temperature (°C)": temperature,
                            "Humidity (%)": humidity,
                            "Rainfall (mm)": rainfall,
                            "Groundwater Depth (m)": groundwater_level,
                            "Annual Recharge (m³/year)": recharge_rate
                        },
                        "optimization": optimization_results,
                        "recommendation": recommendation,
                        "top_recommendations": top_recommendations
                    }

                    st.session_state["farm_step"] = 1

                    st.success(
                        "Analysis generated! Open Insights & Results "
                        "to view your crop recommendation."
                    )

                except Exception as error:

                    st.error(
                        f"Could not generate the analysis: {error}"
                    )


# ============================================================
# INSIGHTS AND RESULTS
# ============================================================

elif page == "📊 Insights & Results":

    hero(
        "Your farm insights",
        "Compare yield, estimated economics, irrigation demand "
        "and groundwater pressure.",
        "ANALYSIS DASHBOARD"
    )

    results = st.session_state.get("agritwin_results")

    if not results:

        st.info("Please complete Farm Analysis first.")

    else:

        recommendation = results.get("recommendation")

        # Support both old and new recommendation result formats.
        saved_recommendations = results.get("top_recommendations", [])
        top_recommendations = []

        for i, item in enumerate(saved_recommendations):

            crop_name = item.get("Crop") or item.get("crop")

            score = item.get("Overall Score (/100)")

            if score is None and item.get("score") is not None:
                score = float(item["score"]) * 100

            if score is not None:
                score = round(float(score), 2)

            if crop_name:
                top_recommendations.append({
                    "Rank": item.get("Rank", i + 1),
                    "Crop": crop_name,
                    "Overall Score (/100)": score
                })

        if recommendation:
            st.subheader("🌱 Best Crop Recommendation")
            st.success(str(recommendation))

            st.caption(
                results.get("recommendation_reason", "")
            )

        st.caption(
            "The seasonal shortlist is an academic demonstration rule. "
            "Verify local crop suitability before making farming decisions."
        )

        st.subheader("🏆 Top 3 Recommended Crops")

        if top_recommendations:
            recommendation_columns = st.columns(3)

            for col, item in zip(recommendation_columns, top_recommendations):
                with col:
                    score_text = (
                        f"Suitability: {item['Overall Score (/100)']}/100"
                        if item["Overall Score (/100)"] is not None
                        else "Score unavailable"
                    )

                    st.metric(
                        label=f"Rank {item['Rank']}",
                        value=item["Crop"],
                        delta=score_text
                    )
        with st.expander("🔍 Check why each crop is ranked"):

            yield_debug = pd.DataFrame(results["predictions"])
            profit_debug = pd.DataFrame(results["financial"])
            ranking_debug = pd.DataFrame(results["optimization"])

            debug_df = yield_debug[
                ["Crop", "Predicted Yield (tonnes/hectare)"]
            ].merge(
                profit_debug[
                    ["Crop", "Estimated Profit (₹)"]
                ],
                on="Crop"
            ).merge(
                ranking_debug[
                    [
                        "Crop",
                        "Profit Score",
                        "Water Score",
                        "Groundwater Score",
                        "Overall Score (/100)"
                    ]
                ],
                on="Crop"
            )

            st.dataframe(
                debug_df.sort_values(
                    "Overall Score (/100)",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )
        predictions = results["predictions"]

        best_seasonal_crop = (
            top_recommendations[0]
            if top_recommendations
            else None
        )

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            info_card(
                "BEST SEASONAL CROP",
                best_seasonal_crop["Crop"] if best_seasonal_crop else "—",
                (
                    f'Score: {best_seasonal_crop["Overall Score (/100)"]}/100'
                    if best_seasonal_crop else "No recommendation"
                )
            )

        with k2:
            info_card(
                "FARM SIZE",
                f'{results["farm_area"]:.2f} acres',
                f'{results["area_hectares"]:.2f} hectares'
            )

        with k3:
            info_card(
                "SEASONAL CROPS COMPARED",
                str(len(results.get("eligible_crops", []))),
                results.get("season", "Selected season")
            )

        with k4:
            profit_best = (
                results["financial"][0]
                if results["financial"]
                else None
            )

            info_card(
                "TOP EST. PROFIT",
                (
                    f'₹{profit_best["Estimated Profit (₹)"]:,.0f}'
                    if profit_best else "—"
                ),
                profit_best["Crop"] if profit_best else "No profit estimate"
            )

        # ----------------------------------------------------
        # YIELD
        # ----------------------------------------------------

        st.markdown("### 🌾 Crop yield comparison")

        yield_df = pd.DataFrame(predictions)

        st.bar_chart(
            yield_df.set_index("Crop")[
                "Predicted Yield (tonnes/hectare)"
            ],
            color="#278653"
        )

        st.dataframe(
            yield_df,
            use_container_width=True,
            hide_index=True
        )

        tab_y, tab_p, tab_w, tab_g, tab_f = st.tabs([
            "Yield",
            "Profit",
            "Water",
            "Groundwater",
            "Farm profile"
        ])

        with tab_y:

            st.write(
                "Yield estimates from the trained Random Forest pipeline."
            )

            st.dataframe(
                yield_df,
                use_container_width=True,
                hide_index=True
            )

        # ----------------------------------------------------
        # PROFIT
        # ----------------------------------------------------

        with tab_p:

            if results["financial"]:

                profit_df = pd.DataFrame(results["financial"])

                st.bar_chart(
                    profit_df.set_index("Crop")[
                        "Estimated Profit (₹)"
                    ],
                    color="#278653"
                )

                st.dataframe(
                    profit_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No profit estimates available.")

        # ----------------------------------------------------
        # WATER
        # ----------------------------------------------------

        with tab_w:

            if results["water_ready"] and results["water"]:

                water_df = pd.DataFrame([
                    {
                        "Crop": x["crop"],
                        "Water Requirement (mm)": x[
                            "water_requirement_mm"
                        ],
                        "Effective Rainfall (mm)": x[
                            "effective_rainfall_mm"
                        ],
                        "Irrigation Volume (m³)": x[
                            "irrigation_requirement_m3"
                        ]
                    }
                    for x in results["water"]
                ])

                st.bar_chart(
                    water_df.set_index("Crop")[
                        "Irrigation Volume (m³)"
                    ],
                    color="#278653"
                )

                st.dataframe(
                    water_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "Enter positive seasonal water requirements "
                    "for all six crops."
                )

        # ----------------------------------------------------
        # GROUNDWATER
        # ----------------------------------------------------

        with tab_g:

            if results["groundwater"]:

                groundwater_df = pd.DataFrame(
                    results["groundwater"]
                )

                st.dataframe(
                    groundwater_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.warning(
                    "Prototype limitation: the current ratio is "
                    "seasonal irrigation demand divided by annual "
                    "recharge. Risk bands are provisional."
                )

            else:

                st.info(
                    "Groundwater estimates will appear after "
                    "valid water and recharge inputs."
                )

        # ----------------------------------------------------
        # FARM PROFILE
        # ----------------------------------------------------

        with tab_f:

            summary = pd.DataFrame(
                list(results["farm_summary"].items()),
                columns=["Parameter", "Entered value"]
            )

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇️ Download farm summary (CSV)",
                data=summary.to_csv(index=False).encode("utf-8"),
                file_name="agritwin_farm_summary.csv",
                mime="text/csv"
            )

        st.caption(
            "All values are estimates based on entered assumptions "
            "and the academic training dataset. They are not a "
            "substitute for local agronomic, hydrological or "
            "financial advice."
        )
