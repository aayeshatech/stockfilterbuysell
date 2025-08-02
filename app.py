"""Astro-Trading Dashboard (Simplified Version)"""
import streamlit as st
import pandas as pd

def get_sample_transit_data():
    """Generate sample planetary transit data"""
    return pd.DataFrame({
        "Planet": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
        "Time": ["00:00:00"]*7,
        "Motion": ["Direct", "Direct", "Direct", "Retrograde", "Direct", "Direct", "Direct"],
        "Zodiac": ["Capricorn", "Gemini", "Gemini", "Sagittarius", "Pisces", "Capricorn", "Aquarius"],
        "Degree": [280, 60, 75, 240, 350, 290, 320],
        "Nakshatra": ["Uttara Ashadha", "Ardra", "Punarvasu", "Purva Ashadha", "Revati", "Uttara Ashadha", "Purva Bhadrapada"],
        "Pada": [4, 1, 1, 3, 4, 4, 2]
    })

def display_transits(transits):
    """Display transit data with styling"""
    st.subheader("Current Planetary Positions")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Retrograde Planets")
        retrograde = transits[transits["Motion"] == "Retrograde"]
        if not retrograde.empty:
            for _, planet in retrograde.iterrows():
                st.warning(f"🔴 {planet['Planet']} in {planet['Zodiac']} ({planet['Nakshatra']} Pada {planet['Pada']})")
        else:
            st.info("No planets in retrograde")
    
    with col2:
        st.markdown("### Direct Motion Planets")
        direct = transits[transits["Motion"] == "Direct"]
        for _, planet in direct.iterrows():
            st.success(f"🔵 {planet['Planet']} in {planet['Zodiac']} ({planet['Nakshatra']} Pada {planet['Pada']})")
    
    st.subheader("Detailed Transit Data")
    st.dataframe(transits)

def main():
    st.set_page_config(
        page_title="Astro-Trading Dashboard",
        layout="wide",
        page_icon="♋"
    )
    
    st.title("🌌 Planetary Transit Analysis")
    
    transits = get_sample_transit_data()
    display_transits(transits)

if __name__ == "__main__":
    main()
