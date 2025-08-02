import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Planetary Data
PLANETARY_DATA = {
    "2025-07-31": {
        "retrograde": ["Mercury"],
        "transits": [
            {"planet": "Sun", "sign": "Cancer", "nakshatra": "Ashlesha", "sectors": ["Oil", "Shipping"]},
            {"planet": "Mars", "sign": "Taurus", "nakshatra": "Rohini", "sectors": ["Metals", "Agriculture"]}
        ],
        "aspects": [
            {"time": "11:00 AM-1:00 PM", "aspect": "Moon sextile Venus", "quality": "Good"},
            {"time": "After 3:00 PM", "aspect": "Mars square Saturn", "quality": "Avoid"}
        ]
    }
}

# Stock Database
STOCKS_DB = [
    {"symbol": "RELIANCE", "sector": "Oil", "nakshatra": "Ashlesha"},
    {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"}
]

def get_recommendations(date):
    date_str = date.strftime("%Y-%m-%d")
    data = PLANETARY_DATA.get(date_str, {})
    
    if not data:
        return None, None, None
    
    # Find favorable sectors
    favorable_sectors = set()
    for transit in data.get("transits", []):
        favorable_sectors.update(transit.get("sectors", []))
    
    # Match stocks to sectors
    recommendations = []
    for stock in STOCKS_DB:
        if stock["sector"] in favorable_sectors:
            strength = "Strong" if any(
                transit["nakshatra"] == stock["nakshatra"]
                for transit in data.get("transits", [])
            ) else "Moderate"
            
            recommendations.append({
                "Symbol": stock["symbol"],
                "Sector": stock["sector"],
                "Signal": "BUY",
                "Strength": strength,
                "Planet": next(
                    (t["planet"] for t in data["transits"] 
                    if stock["sector"] in t["sectors"]),
                    "None"
                ),
                "Nakshatra": stock["nakshatra"]
            })
    
    return data.get("retrograde", []), recommendations, data.get("aspects", [])

def main():
    st.set_page_config(page_title="Astro Stock Advisor", layout="wide")
    st.title("✨ Astrological Stock Advisor")
    
    selected_date = st.date_input(
        "Select Date for Analysis",
        value=datetime(2025, 7, 31)
    )
    
    retrograde, recommendations, aspects = get_recommendations(selected_date)
    
    # Display results
    if recommendations:
        st.dataframe(pd.DataFrame(recommendations))
    
    st.caption(f"Analysis for {selected_date.strftime('%B %d, %Y')}")

if __name__ == "__main__":
    main()
