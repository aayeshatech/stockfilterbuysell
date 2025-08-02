import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Planetary data database (would normally be in a separate file)
PLANETARY_DATA = {
    "2025-08-02": {
        "retrograde": ["Mercury"],
        "transits": [
            {"planet": "Sun", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "sectors": ["Energy", "Government"]},
            {"planet": "Jupiter", "sign": "Pisces", "nakshatra": "Revati", "sectors": ["Pharma", "Banking"]}
        ],
        "aspects": [
            {"time": "9:30-11:30 AM", "aspect": "Moon trine Jupiter", "quality": "Favorable"},
            {"time": "All day", "aspect": "Venus square Saturn", "quality": "Avoid"}
        ]
    },
    "2025-08-06": {
        "retrograde": ["Mercury"],
        "transits": [
            {"planet": "Sun", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "sectors": ["Energy", "Government"]},
            {"planet": "Mars", "sign": "Gemini", "nakshatra": "Ardra", "sectors": ["Metals", "Technology"]}
        ],
        "aspects": [
            {"time": "Afternoon", "aspect": "Sun conjunct Jupiter", "quality": "Excellent"},
            {"time": "Morning", "aspect": "Moon opposite Mars", "quality": "Volatile"}
        ]
    }
}

# Stock database
STOCKS_DB = [
    {"symbol": "RELIANCE", "sector": "Energy", "nakshatra": "Uttara Ashadha"},
    {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
    {"symbol": "TATASTEEL", "sector": "Metals", "nakshatra": "Rohini"},
    {"symbol": "INFY", "sector": "Technology", "nakshatra": "Hasta"}
]

def get_recommendations(date):
    """Generate recommendations for a specific date"""
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
                "Strength": strength
            })
    
    return data.get("retrograde", []), recommendations, data.get("aspects", [])

def main():
    st.set_page_config(page_title="Astro Stock Advisor", layout="wide")
    st.title("✨ Astrological Stock Advisor")
    
    # Date input
    selected_date = st.date_input(
        "Select Date for Analysis",
        min_value=datetime(2025, 8, 1),
        max_value=datetime(2025, 8, 31),
        value=datetime(2025, 8, 2)
    )
    
    # Get data for selected date
    retrograde, recommendations, aspects = get_recommendations(selected_date)
    
    if retrograde is None:
        st.warning("No planetary data available for selected date")
        return
    
    # Display warnings
    with st.expander("⚠️ Planetary Warnings", expanded=True):
        for planet in retrograde:
            st.error(f"{planet} Retrograde: Exercise caution in new investments")
    
    # Display recommendations
    st.subheader("💎 Recommended Stocks")
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(
            rec_df.style.applymap(
                lambda x: "color: green" if x == "BUY" else "",
                subset=["Signal"]
            ),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No strong recommendations for this date")
    
    # Display trading times
    st.subheader("⏰ Favorable Trading Times")
    if aspects:
        aspect_df = pd.DataFrame(aspects)
        # Add emoji based on quality
        aspect_df["Quality"] = aspect_df["quality"].apply(
            lambda x: "✔️ " + x if x == "Favorable" 
            else "❌ " + x if x == "Avoid" 
            else "⭐ " + x
        )
        st.dataframe(
            aspect_df[["time", "Quality", "aspect"]].rename(
                columns={"time": "Time", "aspect": "Planetary Aspect"}
            ),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No significant aspects for this date")
    
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
