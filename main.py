
import streamlit as st
import pandas as pd
import json
from PyPDF2 import PdfReader
from generate_report import generate_report

st.set_page_config(page_title="Market Valuation App", layout="wide")
st.title("🏡 Market Valuation App")
st.markdown("Upload MLS data, apply schema-driven adjustments, and generate a valuation report.")

# Upload schema and MLS data
mls_file = st.file_uploader("Upload MLS CSV/XLSX", type=["csv", "xlsx"])
uploaded_pdf = st.file_uploader("Upload PDF (optional)", type=["pdf"])
schema_file = "market_adjustment_schema.json"

# Manual subject property inputs
subject_info = {}
subject_info["address"] = st.text_input("Subject Address")
subject_info["price"] = st.number_input("Estimated Subject Value ($)", min_value=100000, step=10000)
subject_info["sqft"] = st.number_input("Above Grade SF", min_value=500, step=10)
subject_info["bedrooms"] = st.number_input("Bedrooms", min_value=1, step=1)
subject_info["bathrooms"] = st.number_input("Bathrooms", min_value=1, step=1)
subject_info["garage"] = st.number_input("Garage Bays", min_value=0, step=1)

# Automated Valuation Inputs
col1, col2 = st.columns(2)
with col1:
    subject_info["zestimate"] = st.number_input("Zillow Estimate", min_value=0, step=1000)
with col2:
    subject_info["redfin"] = st.number_input("Redfin Estimate", min_value=0, step=1000)

# PDF Parsing
real_avm = ""
if uploaded_pdf and st.button("Extract AVM from PDF"):
    try:
        reader = PdfReader(uploaded_pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        for line in text.split("\n"):
            if "RealAVM" in line:
                real_avm = line.strip()
                break
        if real_avm:
            st.success(f"Extracted AVM from PDF: {real_avm}")
    except Exception as e:
        st.warning("Could not extract AVM from PDF.")

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

# Process MLS data and generate report
if mls_file:
    df = pd.read_csv(mls_file) if mls_file.name.endswith("csv") else pd.read_excel(mls_file)
    
    # Filter AG SF comps within 85–110%
    ag_low, ag_high = subject_info["sqft"] * 0.85, subject_info["sqft"] * 1.10
    filtered = df[(df["Above Grade Finished Area"] >= ag_low) & (df["Above Grade Finished Area"] <= ag_high)].copy()

    if filtered.empty:
        st.warning("No comps found within AG SF range.")
    else:
        st.success(f"{len(filtered)} comps found within AG SF range.")

        
        # Determine subject value using available sources
        value_sources = []
        if subject_info.get("price", 0) > 0:
            value_sources.append(subject_info["price"])
        if real_avm:
            try:
                real_avm_value = float(''.join(filter(str.isdigit, real_avm)))
                value_sources.append(real_avm_value)
            except:
                pass
        if subject_info.get("zestimate", 0) > 0:
            value_sources.append(subject_info["zestimate"])
        if subject_info.get("redfin", 0) > 0:
            value_sources.append(subject_info["redfin"])
        if value_sources:
            subject_info["final_estimate"] = round(sum(value_sources) / len(value_sources))
            st.info(f"📌 Averaged Subject Value: ${subject_info['final_estimate']:,}")
        else:
            st.warning("⚠️ No subject value inputs provided to calculate average.")

        if st.button("Generate Report", type="primary"):
            try:
                report_path = generate_report(filtered, subject_info)
                with open(report_path, "rb") as file:
                    st.download_button("Download Report", file, file_name="MarketValuationReport.docx")
            except Exception as e:
                st.error(f"Error generating report: {e}")
