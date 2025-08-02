"""Advanced Astro-Trading Dashboard with Watchlist & Time-Based Signals"""

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import logging
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================
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

# Sample transit data - replace with your actual data source
TRANSIT_DATA = {
    "2025-08-04": [
        ["Me", "00:55:55", "R", "Mo", "Sa", "Ma", "Cancer", "Pushya", 3, "12°53'19\"", 13.96],
        ["Mo", "01:31:40", "D", "Ma", "Sa", "Ra", "Scorpio", "Anuradha", 3, "12°53'20\"", -26.47],
        ["Mo", "05:30:19", "D", "Ma", "Sa", "Ju", "Scorpio", "Anuradha", 4, "14°53'20\"", -26.84],
        ["Ve", "08:03:03", "D", "Me", "Ra", "Sa", "Gemini", "Ardra", 2, "10°26'40\"", 22.00],
        ["Mo", "09:01:57", "D", "Ma", "Me", "Me", "Scorpio", "Jyeshtha", 1, "16°40'00\"", -27.13],
        ["Mo", "12:46:17", "D", "Ma", "Me", "Ke", "Scorpio", "Jyeshtha", 1, "18°33'20\"", -27.42],
        ["Mo", "14:18:29", "D", "Ma", "Me", "Ve", "Scorpio", "Jyeshtha", 1, "19°20'00\"", -27.53],
        ["Mo", "18:41:22", "D", "Ma", "Me", "Su", "Scorpio", "Jyeshtha", 2, "21°33'20\"", -27.81],
        ["Mo", "20:00:05", "D", "Ma", "Me", "Mo", "Scorpio", "Jyeshtha", 2, "22°13'20\"", -27.88],
        ["Mo", "22:11:05", "D", "Ma", "Me", "Ma", "Scorpio", "Jyeshtha", 3, "23°20'00\"", -28.00],
        ["Mo", "23:42:40", "D", "Ma", "Me", "Ra", "Scorpio", "Jyeshtha", 3, "24°06'40\"", -28.07]
    ],
    "2025-08-05": [
        ["Su", "00:15:00", "D", "Le", "Mo", "Ju", "Leo", "Magha", 1, "0°00'00\"", 0.0],
        ["Me", "02:30:00", "R", "Mo", "Sa", "Ma", "Cancer", "Pushya", 4, "29°59'59\"", 14.0]
    ]
}

# ================== CORE FUNCTIONS ==================
def get_transit_data(date: datetime) -> pd.DataFrame:
    """Get planetary transit data for selected date"""
    date_str = date.strftime("%Y-%m-%d")
    if date_str in TRANSIT_DATA:
        data = TRANSIT_DATA[date_str]
        return pd.DataFrame(data, columns=[
            "Planet", "Time", "Motion", "Sign Lord", "Star Lord", "Sub Lord",
            "Zodiac", "Nakshatra", "Pada", "Pos in Zodiac", "Declination"
        ])
    return pd.DataFrame()

def get_planet_strength(planet: str, zodiac: str, nakshatra: str, pada: int) -> float:
    """Calculate planetary strength based on Vedic astrology"""
    strength = 0.5  # Base strength
    
    # Exaltation and debilitation
    exaltations = {
        "Sun": ("Aries", 10), "Moon": ("Taurus", 3), 
        "Mars": ("Capricorn", 28), "Mercury": ("Virgo", 15),
        "Jupiter": ("Cancer", 5), "Venus": ("Pisces", 27),
        "Saturn": ("Libra", 20)
    }
    
    debilitations = {
        "Sun": ("Libra", 10), "Moon": ("Scorpio", 3),
        "Mars": ("Cancer", 28), "Mercury": ("Pisces", 15),
        "Jupiter": ("Capricorn", 5), "Venus": ("Virgo", 27),
        "Saturn": ("Aries", 20)
    }
    
    if planet in exaltations and zodiac == exaltations[planet][0]:
        strength = 0.9
    elif planet in debilitations and zodiac == debilitations[planet][0]:
        strength = 0.1
    
    # Nakshatra adjustments
    favorable_nakshatras = ["Pushya", "Rohini", "Uttara Phalguni", "Uttara Ashadha"]
    unfavorable_nakshatras = ["Mula", "Ardra", "Ashlesha", "Jyestha"]
    
    if nakshatra in favorable_nakshatras:
        strength = min(1.0, strength + 0.2)
    elif nakshatra in unfavorable_nakshatras:
        strength = max(0.1, strength - 0.2)
    
    return strength

def analyze_transits(transits: pd.DataFrame) -> Dict:
    """Analyze transits for trading signals"""
    analysis = {
        "bullish_planets": [],
        "bearish_planets": [],
        "key_events": [],
        "time_signals": []
    }
    
    for _, row in transits.iterrows():
        planet = row["Planet"]
        zodiac = row["Zodiac"]
        nakshatra = row["Nakshatra"]
        pada = row["Pada"]
        time_str = row["Time"]
        
        strength = get_planet_strength(planet, zodiac, nakshatra, pada)
        
        if strength > 0.7:
            analysis["bullish_planets"].append(planet)
            signal = "BUY"
        elif strength < 0.3:
            analysis["bearish_planets"].append(planet)
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # Create time-based signals
        analysis["time_signals"].append({
            "time": time_str,
            "planet": planet,
            "signal": signal,
            "strength": strength,
            "reason": f"{planet} in {zodiac} ({nakshatra} pada {pada})"
        })
        
        # Check for special events
        if row["Motion"] == "R":
            analysis["key_events"].append(f"Retrograde {planet}")
    
    return analysis

def get_stock_recommendations(watchlist: List[str], analysis: Dict) -> List[Dict]:
    """Generate stock recommendations based on watchlist and analysis"""
    recommendations = []
    
    for symbol in watchlist:
        planet = PLANET_MAPPING.get(symbol, None)
        if not planet:
            continue
            
        for signal in analysis["time_signals"]:
            if signal["planet"] == planet:
                recommendations.append({
                    "symbol": symbol,
                    "action": signal["signal"],
                    "time": signal["time"],
                    "planet": planet,
                    "strength": signal["strength"],
                    "reason": signal["reason"]
                })
    
    return recommendations

@st.cache_data(ttl=60)
def get_stock_price(symbol: str) -> Optional[float]:
    """Get current stock price"""
    try:
        ticker = yf.Ticker(symbol.replace("^", "").replace("=F", ""))
        data = ticker.history(period="1d", interval="1m")
        return float(data["Close"].iloc[-1]) if not data.empty else None
    except:
        return None

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Astro-Trading Pro",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("♋ Planetary Transit Trader")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")
        analysis_date = st.date_input("Select Date", datetime.now())
        live_mode = st.checkbox("Live Market Data", True)
        
        st.header("Watchlist Management")
        watchlist = st.text_area(
            "Enter your watchlist (one symbol per line)",
            "\n".join(DEFAULT_SYMBOLS),
            height=200
        )
        watchlist = [s.strip() for s in watchlist.split("\n") if s.strip()]
    
    # Main dashboard
    tab1, tab2, tab3 = st.tabs(["Transit Timeline", "Stock Signals", "Watchlist Analysis"])
    
    # Get and analyze transit data
    transit_data = get_transit_data(analysis_date)
    analysis = analyze_transits(transit_data)
    
    with tab1:
        st.subheader(f"Planetary Transits for {analysis_date.strftime('%Y-%m-%d')}")
        
        if transit_data.empty:
            st.warning("No transit data available for selected date")
        else:
            st.dataframe(transit_data, use_container_width=True)
            
            st.subheader("Key Events")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Bullish Planets**")
                for planet in analysis["bullish_planets"]:
                    st.write(f"- {planet}")
            with col2:
                st.write("**Bearish Planets**")
                for planet in analysis["bearish_planets"]:
                    st.write(f"- {planet}")
            
            if analysis["key_events"]:
                st.write("**Special Events**")
                for event in analysis["key_events"]:
                    st.write(f"- {event}")
    
    with tab2:
        st.subheader("Time-Based Trading Signals")
        recommendations = get_stock_recommendations(watchlist, analysis)
        
        if not recommendations:
            st.info("No strong signals for your watchlist today")
        else:
            # Group by time
            time_groups = {}
            for rec in recommendations:
                if rec["time"] not in time_groups:
                    time_groups[rec["time"]] = []
                time_groups[rec["time"]].append(rec)
            
            # Display by time
            for time_str, recs in sorted(time_groups.items()):
                with st.expander(f"Time: {time_str}"):
                    for rec in recs:
                        col1, col2, col3 = st.columns([1, 2, 3])
                        with col1:
                            color = "green" if rec["action"] == "BUY" else "red"
                            st.markdown(f"**<span style='color:{color}'>{rec['action']}</span>**", 
                                      unsafe_allow_html=True)
                        with col2:
                            st.write(f"**{rec['symbol']}**")
                        with col3:
                            st.write(rec["reason"])
                            
                            if live_mode:
                                price = get_stock_price(rec["symbol"])
                                if price:
                                    st.write(f"Price: ${price:,.2f}")
    
    with tab3:
        st.subheader("Watchlist Planetary Analysis")
        
        if not watchlist:
            st.warning("Please add symbols to your watchlist")
        else:
            for symbol in watchlist:
                planet = PLANET_MAPPING.get(symbol, None)
                if not planet:
                    continue
                    
                planet_signals = [s for s in analysis["time_signals"] if s["planet"] == planet]
                
                with st.expander(f"{symbol} ({planet})"):
                    if not planet_signals:
                        st.write("No significant transits for this planet")
                    else:
                        for signal in planet_signals:
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                color = "green" if signal["signal"] == "BUY" else "red" if signal["signal"] == "SELL" else "gray"
                                st.markdown(f"**<span style='color:{color}'>{signal['signal']}</span> @ {signal['time']}**", 
                                          unsafe_allow_html=True)
                            with col2:
                                st.write(signal["reason"])
                                st.progress(signal["strength"])

if __name__ == "__main__":
    main()
