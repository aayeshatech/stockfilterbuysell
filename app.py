import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Extended Planetary Data for August 2025
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
    },
    "2025-08-01": {
        "retrograde": ["Mercury"],
        "transits": [
            {"planet": "Sun", "sign": "Leo", "nakshatra": "Magha", "sectors": ["Entertainment", "Gold"]},
            {"planet": "Venus", "sign": "Gemini", "nakshatra": "Ardra", "sectors": ["Technology", "Communication"]}
        ],
        "aspects": [
            {"time": "Market Open", "aspect": "Sun trine Jupiter", "quality": "Excellent"},
            {"time": "Afternoon", "aspect": "Mercury opposite Pluto", "quality": "Volatile"}
        ]
    }
}

# Extended Stock Database
STOCKS_DB = [
    {"symbol": "RELIANCE", "sector": "Oil", "nakshatra": "Ashlesha"},
    {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
    {"symbol": "TATASTEEL", "sector": "Metals", "nakshatra": "Rohini"}
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
                "Strength": strength,
                "Planet": next(
                    (t["planet"] for t in data["transits"] 
                    if stock["sector"] in t["sectors"]),
                "Nakshatra": stock["nakshatra"]
            })
    
    return data.get("retrograde", []), recommendations, data.get("aspects", [])

def main():
    st.set_page_config(page_title="Astro Stock Advisor", layout="wide")
    st.title("✨ Astrological Stock Advisor")
    
    # Date input with default to current date
    selected_date = st.date_input(
        "Select Date for Analysis",
        min_value=datetime(2025, 7, 1),
        max_value=datetime(2025, 8, 31),
        value=datetime(2025, 8, 2)
    )
    
    # Get data for selected date
    retrograde, recommendations, aspects = get_recommendations(selected_date)
    
    # Display warnings
    with st.expander("⚠️ Planetary Warnings", expanded=True):
        if retrograde:
            for planet in retrograde:
                st.error(f"{planet} Retrograde: Exercise caution in new investments")
        else:
            st.success("No retrograde planets - Generally favorable day")
    
    # Display recommendations
    st.subheader("💎 Recommended Stocks")
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        
        # Color formatting
        def color_strength(val):
            color = 'green' if val == 'Strong' else 'orange'
            return f'color: {color}'
        
        st.dataframe(
            rec_df.style.applymap(color_strength, subset=['Strength']),
            column_config={
                "Symbol": st.column_config.TextColumn(width="small"),
                "Planet": st.column_config.TextColumn("Dominant Planet"),
                "Nakshatra": st.column_config.TextColumn("Lunar Mansion")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No strong recommendations for this date")
    
    # Display trading times
    st.subheader("⏰ Planetary Aspects & Trading Times")
    if aspects:
        aspect_df = pd.DataFrame(aspects)
        
        # Quality indicators
        def quality_icon(quality):
            if "Excellent" in quality: return "⭐"
            if "Good" in quality: return "✔️" 
            if "Avoid" in quality: return "❌"
            return ""
        
        aspect_df["Quality"] = aspect_df["quality"].apply(
            lambda x: f"{quality_icon(x)} {x}")
        
        st.dataframe(
            aspect_df[["time", "Quality", "aspect"]].rename(
                columns={"time": "Time", "aspect": "Planetary Aspect"}
            ),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No significant aspects recorded for this date")
    
    st.caption(f"Analysis for {selected_date.strftime('%B %d, %Y')}")

if __name__ == "__main__":
    main()
