import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Market Valuation App", layout="wide")

st.title("🏡 Market Valuation App")
st.markdown("Upload MLS data, apply schema-driven adjustments, and generate a valuation report.")

# Uploads
mls_file = st.file_uploader("Upload MLS CSV/XLSX", type=["csv", "xlsx"])
schema_file = "market_adjustment_schema.json"

# Manual Inputs
subject_price = st.number_input("Estimated Subject Value", min_value=100000, step=10000)
subject_ag = st.number_input("Above Grade SF", step=10)
subject_beds = st.number_input("Bedrooms", step=1)
subject_baths = st.number_input("Bathrooms", step=1)
subject_garage = st.number_input("Garage Bays", step=1)

# Load Schema
with open(schema_file, "r") as f:
    schema = json.load(f)

st.success("Schema loaded successfully. AG, Basement, and Garage adjustments are tiered.")

if mls_file:
    if mls_file.name.endswith(".csv"):
        df = pd.read_csv(mls_file)
    else:
        df = pd.read_excel(mls_file)
    st.write("### Sample MLS Data", df.head())
    # Placeholder for comp filtering, adjustment logic, and summary
    st.info("Valuation calculations coming next...")
else:
    st.warning("Upload an MLS file to begin.")
