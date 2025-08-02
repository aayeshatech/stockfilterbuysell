"""Astro-Trading Dashboard with Real-time Planetary Data"""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from typing import Dict, List

# Configure API - replace with your actual API key
ASTRONOMICS_API = "https://data.astronomics.ai/almanac/"
HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}

# Default symbols and planet mappings
DEFAULT_SYMBOLS = [
    "GC=F", "SI=F", "CL=F", "NG=F", 
    "BTC-USD", "^DJI", "^GSPC", "^IXIC",
    "AAPL", "MSFT", "TSLA", "NVDA", "AMZN"
]

PLANET_MAPPING = {
    "GC=F": "Sun", "SI=F": "Moon", "CL=F": "Mars", "NG=F": "Venus",
    "BTC-USD": "Uranus", "^DJI": "Jupiter", "^GSPC": "Saturn", 
    "^IXIC": "Mercury", "AAPL": "Mercury", "MSFT": "Saturn",
    "TSLA": "Uranus", "NVDA": "Mars", "AMZN": "Jupiter"
}

@st.cache_data(ttl=3600)
def fetch_transit_data(date: datetime) -> pd.DataFrame:
    """Fetch planetary transit data from API"""
    date_str = date.strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{ASTRONOMICS_API}{date_str}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        transits = []
        for planet_data in data.get("planets", []):
            transits.append({
                "Planet": planet_data["name"],
                "Time": planet_data["time"],
                "Zodiac": planet_data["zodiac"]["sign"],
                "Degree": planet_data["zodiac"]["degree"],
                "Nakshatra": planet_data["nakshatra"]["name"],
                "Pada": planet_data["nakshatra"]["pada"],
                "Motion": "R" if planet_data.get("is_retrograde", False) else "D",
                "House": planet_data.get("house", 1),
                "Declination": planet_data.get("declination", 0)
            })
        return pd.DataFrame(transits)
    except Exception as e:
        st.error(f"Failed to fetch transit data: {str(e)}")
        return pd.DataFrame()

def plot_planetary_positions(transits: pd.DataFrame):
    """Create polar plot of planetary positions"""
    fig = go.Figure()
    
    for _, row in transits.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["Degree"]],
            theta=[row["Zodiac"]],
            name=row["Planet"],
            marker=dict(
                size=20,
                color="red" if row["Motion"] == "R" else "blue",
                line=dict(width=2, color="DarkSlateGrey")
            ),
            hovertemplate=f"<b>{row['Planet']}</b><br>"
                        f"Zodiac: {row['Zodiac']}<br>"
                        f"Degree: {row['Degree']}°<br>"
                        f"Nakshatra: {row['Nakshatra']} (Pada {row['Pada']})<br>"
                        f"Motion: {'Retrograde' if row['Motion'] == 'R' else 'Direct'}<extra></extra>"
        ))
    
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                period=360,
                tickvals=list(range(0, 360, 30))
        ),
        radialaxis=dict(visible=False),
        showlegend=True,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Astro-Trading Dashboard",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌌 Planetary Transit Trading System")
    
    with st.sidebar:
        st.header("Configuration")
        analysis_date = st.date_input("Select Date", datetime.now())
        
        st.header("Watchlist")
        watchlist = st.text_area(
            "Enter symbols (one per line)",
            "\n".join(DEFAULT_SYMBOLS),
            height=200
        )
        watchlist = [s.strip() for s in watchlist.split("\n") if s.strip()]
    
    transits = fetch_transit_data(analysis_date)
    
    if not transits.empty:
        plot_planetary_positions(transits)
        st.dataframe(transits, use_container_width=True)
    else:
        st.warning("No transit data available for selected date")

if __name__ == "__main__":
    main()
