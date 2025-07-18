import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Market Valuation App", layout="wide")
st.title("🏡 Market Valuation App")
st.markdown("Upload MLS data, apply schema-driven adjustments, and generate a valuation report.")

# Upload schema and MLS data
mls_file = st.file_uploader("Upload MLS CSV/XLSX", type=["csv", "xlsx"])
schema_file = "market_adjustment_schema.json"

# Manual subject property inputs
subject_price = st.number_input("Estimated Subject Value ($)", min_value=100000, step=10000)
subject_ag = st.number_input("Above Grade SF", min_value=500, step=10)
subject_beds = st.number_input("Bedrooms", min_value=1, step=1)
subject_baths = st.number_input("Bathrooms", min_value=1, step=1)
subject_garage = st.number_input("Garage Bays", min_value=0, step=1)

# Load schema
with open(schema_file, "r") as f:
    schema = json.load(f)

# Select price tier for AG/Basement adjustments
price_tiers = schema["squareFootageAdjustments"]
selected_tier = None
for tier in price_tiers:
    if "$700K" in tier["priceRange"]:
        selected_tier = tier
        break

ag_rate = selected_tier["aboveGrade"][0] if isinstance(selected_tier["aboveGrade"], list) else selected_tier["aboveGrade"]
basement_finished_rate = selected_tier["basementFinished"][0] if isinstance(selected_tier["basementFinished"], list) else selected_tier["basementFinished"]
basement_unfinished_rate = selected_tier["basement"] if isinstance(selected_tier["basement"], int) else selected_tier["basement"][0]

if mls_file:
    df = pd.read_csv(mls_file) if mls_file.name.endswith("csv") else pd.read_excel(mls_file)
    st.subheader("📊 Raw MLS Data Preview")
    st.dataframe(df.head())

    # Filter AG SF comps within 85–110%
    ag_low, ag_high = subject_ag * 0.85, subject_ag * 1.10
    filtered = df[(df["Above Grade Finished Area"] >= ag_low) & (df["Above Grade Finished Area"] <= ag_high)].copy()

    if filtered.empty:
        st.warning("No comps found within AG SF range.")
    else:
        # Calculate AG, Basement Adjustments
        filtered["AG_Diff"] = filtered["Above Grade Finished Area"] - subject_ag
        filtered["AG_Adjustment"] = filtered["AG_Diff"] * ag_rate

        filtered["Finished_Bsmt"] = filtered.get("Below Grade Finished Area", 0).fillna(0)
        filtered["Unfinished_Bsmt"] = filtered.get("Below Grade Unfinished Area", 0).fillna(0)
        filtered["Basement_Adjustment"] = (
            filtered["Finished_Bsmt"] * basement_finished_rate +
            filtered["Unfinished_Bsmt"] * basement_unfinished_rate
        )

        # Total and adjusted price
        filtered["Total_Adjustment"] = filtered["AG_Adjustment"] + filtered["Basement_Adjustment"]
        filtered["Adjusted_Price"] = filtered["Close Price"] - filtered["Total_Adjustment"]
        filtered["Adjusted PPSF"] = filtered["Adjusted_Price"] / subject_ag

        st.subheader("🧮 Adjusted Comparable Sales")
        st.dataframe(filtered[[
            "Close Price", "Above Grade Finished Area", "Finished_Bsmt", "Unfinished_Bsmt",
            "AG_Adjustment", "Basement_Adjustment", "Total_Adjustment", "Adjusted_Price", "Adjusted PPSF"
        ]])

        # Summary stats
        st.subheader("📈 Valuation Summary")
        min_val = int(filtered["Adjusted_Price"].min())
        max_val = int(filtered["Adjusted_Price"].max())
        avg_val = int(filtered["Adjusted_Price"].mean())
        st.success(f"Suggested Market Range: ${min_val:,} – ${max_val:,}")
        st.info(f"Recommended List Price Zone: ${avg_val - 10000:,} – ${avg_val + 10000:,}")
else:
    st.warning("📤 Upload MLS data to begin analysis.")
