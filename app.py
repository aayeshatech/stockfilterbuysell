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
HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}  # Store in Streamlit secrets

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

# ================== DATA FUNCTIONS ==================
@st.cache_data(ttl=3600)
def fetch_transit_data(date: datetime) -> pd.DataFrame:
    """Fetch planetary transit data from astronomics.ai API"""
    date_str = date.strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{ASTRONOMICS_API}{date_str}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Transform API response to DataFrame
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

def calculate_aspects(transits: pd.DataFrame) -> pd.DataFrame:
    """Calculate planetary aspects based on zodiac positions"""
    aspects = []
    for _, p1 in transits.iterrows():
        for _, p2 in transits.iterrows():
            if p1["Planet"] != p2["Planet"]:
                angle = abs(p1["Degree"] - p2["Degree"]) % 360
                if angle < 8:  # Conjunction
                    aspects.append({
                        "Planet1": p1["Planet"],
                        "Planet2": p2["Planet"],
                        "Aspect": "Conjunction",
                        "Orb": angle,
                        "Time": max(p1["Time"], p2["Time"])
                    })
                elif abs(angle - 180) < 8:  # Opposition
                    aspects.append({
                        "Planet1": p1["Planet"],
                        "Planet2": p2["Planet"],
                        "Aspect": "Opposition",
                        "Orb": angle,
                        "Time": max(p1["Time"], p2["Time"])
                    })
                elif abs(angle - 120) < 8:  # Trine
                    aspects.append({
                        "Planet1": p1["Planet"],
                        "Planet2": p2["Planet"],
                        "Aspect": "Trine",
                        "Orb": angle,
                        "Time": max(p1["Time"], p2["Time"])
                    })
    return pd.DataFrame(aspects)

# ================== ANALYSIS FUNCTIONS ==================
def analyze_planetary_strength(transits: pd.DataFrame) -> pd.DataFrame:
    """Analyze planetary strength based on Vedic astrology rules"""
    strengths = []
    for _, row in transits.iterrows():
        strength = 0.5  # Base strength
        
        # Exaltation and debilitation
        exaltations = {
            "Sun": ("Aries", 10), "Moon": ("Taurus", 3),
            "Mars": ("Capricorn", 28), "Mercury": ("Virgo", 15),
            "Jupiter": ("Cancer", 5), "Venus": ("Pisces", 27),
            "Saturn": ("Libra", 20)
        }
        
        if row["Planet"] in exaltations:
            sign, deg = exaltations[row["Planet"]]
            if row["Zodiac"] == sign and abs(row["Degree"] - deg) < 5:
                strength = 0.9
        
        # Retrograde adjustment
        if row["Motion"] == "R":
            strength *= 0.8  # Reduce strength for retrograde
            
        strengths.append(strength)
    
    transits["Strength"] = strengths
    return transits

def generate_trading_signals(watchlist: List[str], transits: pd.DataFrame) -> pd.DataFrame:
    """Generate trading signals based on planetary transits"""
    signals = []
    for symbol in watchlist:
        planet = PLANET_MAPPING.get(symbol)
        if not planet:
            continue
            
        planet_transits = transits[transits["Planet"] == planet]
        for _, transit in planet_transits.iterrows():
            if transit["Strength"] > 0.7:
                action = "BUY"
            elif transit["Strength"] < 0.3:
                action = "SELL"
            else:
                continue
                
            signals.append({
                "Symbol": symbol,
                "Action": action,
                "Time": transit["Time"],
                "Planet": planet,
                "Strength": transit["Strength"],
                "Zodiac": transit["Zodiac"],
                "Nakshatra": transit["Nakshatra"],
                "Pada": transit["Pada"]
            })
    return pd.DataFrame(signals)

# ================== VISUALIZATION ==================
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

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Astro-Trading Dashboard",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌌 Planetary Transit Trading System")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")
        analysis_date = st.date_input("Select Date", datetime.now())
        live_mode = st.checkbox("Live Market Data", True)
        
        st.header("Watchlist")
        watchlist = st.text_area(
            "Enter symbols (one per line)",
            "\n".join(DEFAULT_SYMBOLS),
            height=200
        )
        watchlist = [s.strip() for s in watchlist.split("\n") if s.strip()]
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Planetary Positions", "Trading Signals", "Market Analysis"])
    
    # Fetch and process data
    transits = fetch_transit_data(analysis_date)
    aspects = calculate_aspects(transits)
    transits = analyze_planetary_strength(transits)
    signals = generate_trading_signals(watchlist, transits)
    
    with tab1:
        st.subheader(f"Planetary Positions for {analysis_date.strftime('%Y-%m-%d')}")
        
        if transits.empty:
            st.warning("No transit data available for selected date")
        else:
            plot_planetary_positions(transits)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Planetary Transits")
                st.dataframe(transits, use_container_width=True)
            with col2:
                st.subheader("Planetary Aspects")
                st.dataframe(aspects, use_container_width=True)
    
    with tab2:
        st.subheader("Trading Signals")
        
        if signals.empty:
            st.info("No strong signals for today")
        else:
            # Group signals by time
            signals["Time"] = pd.to_datetime(signals["Time"])
            signals = signals.sort_values("Time")
            
            for time, group in signals.groupby("Time"):
                with st.expander(f"Time: {time.strftime('%H:%M:%S')}"):
                    for _, signal in group.iterrows():
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            color = "green" if signal["Action"] == "BUY" else "red"
                            st.markdown(f"**<span style='color:{color}'>{signal['Action']}</span>**", 
                                      unsafe_allow_html=True)
                        with col2:
                            st.write(f"**{signal['Symbol']}** ({signal['Planet']})")
                            st.write(f"{signal['Zodiac']} - {signal['Nakshatra']} (Pada {signal['Pada']})")
                        with col3:
                            st.metric("Strength", f"{signal['Strength']:.0%}")
                            
                            if live_mode:
                                try:
                                    price = yf.Ticker(signal["Symbol"]).history(period="1d")["Close"].iloc[-1]
                                    st.write(f"Price: ${price:,.2f}")
                                except:
                                    st.write("Price unavailable")
    
    with tab3:
        st.subheader("Market Analysis")
        
        if transits.empty:
            st.warning("No data available for analysis")
        else:
            # Calculate overall market sentiment
            bullish = len(transits[transits["Strength"] > 0.7])
            bearish = len(transits[transits["Strength"] < 0.3])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bullish Planets", bullish)
            with col2:
                st.metric("Bearish Planets", bearish)
            with col3:
                sentiment = "Bullish" if bullish > bearish else "Bearish" if bearish > bullish else "Neutral"
                st.metric("Market Sentiment", sentiment)
            
            # Show retrograde planets
            retrograde = transits[transits["Motion"] == "R"]
            if not retrograde.empty:
                st.subheader("Retrograde Planets")
                for _, planet in retrograde.iterrows():
                    st.warning(f"{planet['Planet']} is retrograde in {planet['Zodiac']}")

if __name__ == "__main__":
    main()
