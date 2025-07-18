# Market Valuation Streamlit App

This application allows real estate professionals to upload MLS comparable data, apply dynamic adjustments using a JSON-based schema, and generate a market valuation summary including adjusted comp pricing, suggested listing range, and downloadable reports.

## 📦 Features

- Upload MLS data (.csv or .xlsx)
- Manual entry of subject property details
- Load JSON-based adjustment schema
- Apply tiered adjustments for:
  - Above Grade SF
  - Basement (Finished/Unfinished)
  - Garage Bays
- Dynamic comp analysis and adjusted price range
- (Coming soon) DOCX report generation

## 📁 File Structure

- `main.py` — Streamlit app entry point
- `market_adjustment_schema.json` — Dynamic pricing and logic schema
- `README.md` — Project overview

## ▶️ To Run

```bash
streamlit run main.py
```

## 🔧 Requirements

- Python 3.9+
- pandas
- streamlit
