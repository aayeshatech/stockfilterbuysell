"""Advanced Astro-Trading Dashboard with Planetary Transit Analysis"""

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import logging
import yfinance as yf
import ephem
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================
GLOBAL_SYMBOLS = [
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

# Vedic Astrology Parameters
NAKSHATRAS = {
    "Ashwini": (0, 13, 20), "Bharani": (13, 20, 26, 40), 
    "Pushya": (93, 20, 106, 40), "Anuradha": (213, 20, 226, 40),
    "Jyeshtha": (226, 40, 240)
}

ZODIAC_SIGNS = {
    "Aries": (0, 30), "Taurus": (30, 60), "Gemini": (60, 90),
    "Cancer": (90, 120), "Leo": (120, 150), "Virgo": (150, 180),
    "Libra": (180, 210), "Scorpio": (210, 240), "Sagittarius": (240, 270)
}

# ================== CORE FUNCTIONS ==================
def get_vedic_analysis(planet: str, degree: float, nakshatra: str, pada: int) -> Dict:
    """Analyze planetary position using Vedic astrology"""
    analysis = {
        "strength": 0.5,
        "sentiment": "Neutral",
        "aspects": []
    }
    
    # Calculate planetary strength
    if planet in ["Sun", "Mars", "Jupiter"]:
        if degree < 15 or degree > 345:
            analysis["strength"] = 0.9  # Exalted
        elif 165 < degree < 195:
            analysis["strength"] = 0.3  # Debilitated
    elif planet in ["Moon", "Venus"]:
        if 60 < degree < 90:
            analysis["strength"] = 0.9
        elif 240 < degree < 270:
            analysis["strength"] = 0.3
    
    # Nakshatra-based analysis
    if nakshatra in ["Pushya", "Rohini", "Uttara Phalguni"]:
        analysis["strength"] = min(1.0, analysis["strength"] + 0.2)
    elif nakshatra in ["Mula", "Ardra"]:
        analysis["strength"] = max(0.1, analysis["strength"] - 0.2)
    
    # Determine market sentiment
    if analysis["strength"] > 0.7:
        analysis["sentiment"] = "Bullish"
    elif analysis["strength"] < 0.3:
        analysis["sentiment"] = "Bearish"
    
    return analysis

@st.cache_data(ttl=3600)
def get_transit_data(date: datetime) -> pd.DataFrame:
    """Get planetary transit data for a specific date"""
    # This would normally connect to your ephemeris database
    # Here we simulate with sample data
    data = {
        "Planet": ["Me", "Mo", "Mo", "Ve", "Mo", "Mo", "Mo", "Mo", "Mo", "Mo"],
        "Date": ["2025-08-04"]*10,
        "Time": ["00:55:55", "01:31:40", "05:30:19", "08:03:03", "09:01:57", 
                "12:46:17", "14:18:29", "18:41:22", "20:00:05", "22:11:05"],
        "Motion": ["R", "D", "D", "D", "D", "D", "D", "D", "D", "D"],
        "Sign Lord": ["Mo", "Ma", "Ma", "Me", "Ma", "Ma", "Ma", "Ma", "Ma", "Ma"],
        "Star Lord": ["Sa", "Sa", "Sa", "Ra", "Me", "Me", "Me", "Me", "Me", "Me"],
        "Sub Lord": ["Ma", "Ra", "Ju", "Sa", "Me", "Ke", "Ve", "Su", "Mo", "Ma"],
        "Zodiac": ["Cancer", "Scorpio", "Scorpio", "Gemini", "Scorpio", 
                  "Scorpio", "Scorpio", "Scorpio", "Scorpio", "Scorpio"],
        "Nakshatra": ["Pushya", "Anuradha", "Anuradha", "Ardra", "Jyeshtha",
                     "Jyeshtha", "Jyeshtha", "Jyeshtha", "Jyeshtha", "Jyeshtha"],
        "Pada": [3, 3, 4, 2, 1, 1, 1, 2, 2, 3],
        "Pos in Zodiac": ["12°53'19\"", "12°53'20\"", "14°53'20\"", "10°26'40\"",
                         "16°40'00\"", "18°33'20\"", "19°20'00\"", "21°33'20\"",
                         "22°13'20\"", "23°20'00\""],
        "Declination": [13.96, -26.47, -26.84, 22.00, -27.13, -27.42, -27.53,
                       -27.81, -27.88, -28.00]
    }
    return pd.DataFrame(data)

def analyze_transits(transits: pd.DataFrame) -> Dict:
    """Analyze transits for trading signals"""
    analysis = {
        "bullish_planets": [],
        "bearish_planets": [],
        "key_events": [],
        "overall_sentiment": "Neutral"
    }
    
    for _, row in transits.iterrows():
        planet = row["Planet"]
        degree = float(row["Pos in Zodiac"].split("°")[0])
        nakshatra = row["Nakshatra"]
        pada = row["Pada"]
        
        vedic = get_vedic_analysis(planet, degree, nakshatra, pada)
        
        if vedic["sentiment"] == "Bullish":
            analysis["bullish_planets"].append(planet)
        elif vedic["sentiment"] == "Bearish":
            analysis["bearish_planets"].append(planet)
            
        # Check for special configurations
        if row["Motion"] == "R" and planet in ["Me", "Ve", "Ma"]:
            analysis["key_events"].append(f"Retrograde {planet}")
            
    # Determine overall sentiment
    bull_count = len(analysis["bullish_planets"])
    bear_count = len(analysis["bearish_planets"])
    
    if bull_count - bear_count >= 2:
        analysis["overall_sentiment"] = "Bullish"
    elif bear_count - bull_count >= 2:
        analysis["overall_sentiment"] = "Bearish"
        
    return analysis

def get_stock_recommendations(sentiment: str, planet_analysis: Dict) -> List[str]:
    """Generate stock recommendations based on astro analysis"""
    recommendations = []
    
    if sentiment == "Bullish":
        for symbol, planet in PLANET_MAPPING.items():
            if planet in planet_analysis["bullish_planets"] and "^" not in symbol:
                recommendations.append((symbol, "BUY"))
                
    elif sentiment == "Bearish":
        for symbol, planet in PLANET_MAPPING.items():
            if planet in planet_analysis["bearish_planets"] and "^" not in symbol:
                recommendations.append((symbol, "SELL"))
                
    # Add additional filters based on planetary aspects
    if "Retrograde Me" in planet_analysis["key_events"]:
        recommendations = [r for r in recommendations if r[1] == "SELL" or "BTC" in r[0]]
    
    return recommendations

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Vedic Astro Trader Pro",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("♋ Vedic Astro-Trading System")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Analysis Parameters")
        analysis_date = st.date_input("Select Date", datetime.now())
        selected_planets = st.multiselect(
            "Focus Planets", 
            ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
            default=["Mercury", "Venus", "Mars"]
        )
        live_mode = st.checkbox("Live Market Data", True)
    
    # Main dashboard
    tab1, tab2, tab3 = st.tabs(["Transit Analysis", "Stock Recommendations", "Planetary Alignments"])
    
    with tab1:
        st.subheader("Planetary Transit Analysis")
        transit_data = get_transit_data(analysis_date)
        analysis = analyze_transits(transit_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Overall Market Sentiment", analysis["overall_sentiment"])
            st.write("**Bullish Planets:**", ", ".join(analysis["bullish_planets"]))
            st.write("**Bearish Planets:**", ", ".join(analysis["bearish_planets"]))
            
        with col2:
            st.write("**Key Events:**")
            for event in analysis["key_events"]:
                st.write(f"- {event}")
        
        st.dataframe(transit_data, use_container_width=True)
    
    with tab2:
        st.subheader("Stock Trading Recommendations")
        recommendations = get_stock_recommendations(
            analysis["overall_sentiment"],
            analysis
        )
        
        if not recommendations:
            st.warning("No strong recommendations based on current planetary positions")
        else:
            for symbol, action in recommendations:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric(symbol, action)
                with col2:
                    if live_mode:
                        try:
                            ticker = yf.Ticker(symbol.replace("^", "").replace("=F", ""))
                            data = ticker.history(period="1d", interval="1m")
                            if not data.empty:
                                current_price = data["Close"].iloc[-1]
                                st.write(f"Current: ${current_price:,.2f}")
                        except:
                            st.write("Price data unavailable")
    
    with tab3:
        st.subheader("Planetary Position Analysis")
        st.write("Detailed Vedic astrology analysis of current planetary positions")
        
        for planet in selected_planets:
            planet_data = transit_data[transit_data["Planet"] == planet[:2]]
            if not planet_data.empty:
                row = planet_data.iloc[0]
                vedic = get_vedic_analysis(
                    planet, 
                    float(row["Pos in Zodiac"].split("°")[0]),
                    row["Nakshatra"],
                    row["Pada"]
                )
                
                with st.expander(f"{planet} Analysis"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Position:** {row['Pos in Zodiac']}")
                        st.write(f"**Nakshatra:** {row['Nakshatra']} (Pada {row['Pada']})")
                        st.write(f"**Motion:** {'Retrograde' if row['Motion'] == 'R' else 'Direct'}")
                    with col2:
                        st.write(f"**Strength:** {vedic['strength']:.1f}/1.0")
                        st.write(f"**Sentiment:** {vedic['sentiment']}")
                        st.write(f"**Zodiac Sign:** {row['Zodiac']}")

if __name__ == "__main__":
    main()
