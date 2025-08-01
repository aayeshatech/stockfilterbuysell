"""
Ultra-Fast Market Astro Signals with Caching and Parallel Processing
"""

import streamlit as st
from datetime import datetime
import pytz
import time
import logging
import yfinance as yf
import ephem
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== LIGHTWEIGHT CONFIG ==================
MARKET_DATA = {
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT"],
    "Commodities": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL"],
    # Reduced for testing - enable more after optimization
}

PLANET_MAPPING = {
    "GOLD": "Sun",
    "SILVER": "Moon",
    "CRUDEOIL": "Mars",
    "RELIANCE": "Jupiter",
    "TATA": "Venus",
    "HDFC": "Mercury"
}

# ================== OPTIMIZED FUNCTIONS ==================
@st.cache_data(ttl=60, show_spinner=False)  # Cache prices for 1 minute
def get_live_price(symbol: str) -> float:
    """Cached price fetch with timeout"""
    try:
        clean_symbol = symbol.split(":")[-1].split("-")[0]
        data = yf.Ticker(clean_symbol).history(period="1d", timeout=5)  # 5-second timeout
        return data["Close"].iloc[-1]
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=32)  # Cache last 32 planet calculations
def get_planet_strength(planet: str, timestamp: float) -> float:
    """Cached planetary strength calculation"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        planet_obj.compute(observer)
        return float(planet_obj.alt / (ephem.pi/2))
    except Exception as e:
        logger.warning(f"Planet calc error: {str(e)}")
        return 0.5

def get_planet(symbol: str) -> str:
    """Fast symbol-to-planet mapping"""
    for key, planet in PLANET_MAPPING.items():
        if key in symbol:
            return planet
    return "Unknown"

def fetch_all_data(symbols: List[str], now: datetime) -> List[Dict]:
    """Parallel data fetching"""
    timestamp = now.timestamp()
    
    def process_symbol(symbol):
        planet = get_planet(symbol)
        strength = get_planet_strength(planet, timestamp)
        price = get_live_price(symbol)
        
        # Simplified signal logic
        if strength > 0.7: signal = "BUY"
        elif strength < 0.3: signal = "SELL"
        else: signal = "HOLD"
        
        return {
            "Symbol": symbol,
            "Price": f"{price:,.2f}",
            "Signal": signal,
            "Confidence": f"{strength:.0%}",
            "Planet": planet,
            "Color": "green" if signal == "BUY" else "red" if signal == "SELL" else "gray"
        }
    
    with ThreadPoolExecutor() as executor:
        return list(executor.map(process_symbol, symbols))

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Turbo Astro Signals",
        layout="wide",
        page_icon="🚀"
    )
    
    # Lightweight UI
    st.title("⚡ Turbo Market Signals")
    st.caption("Real-time optimized planetary analysis")
    
    with st.sidebar:
        market = st.selectbox("Market", list(MARKET_DATA.keys()))
        refresh_rate = st.slider("Refresh (sec)", 10, 60, 30)  # Minimum 10 seconds
        auto_refresh = st.checkbox("Auto Refresh", True)
    
    placeholder = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            signals = fetch_all_data(MARKET_DATA[market], now)
            
            with placeholder.container():
                # Ultra-fast display
                for signal in signals:
                    st.markdown(
                        f"""<div style='background:{signal["Color"]};padding:8px;margin:4px;border-radius:5px;'>
                        <b>{signal["Symbol"]}</b>: {signal["Signal"]} ({signal["Confidence"]})
                        <br>Price: {signal["Price"]} | Planet: {signal["Planet"]}
                        </div>""",
                        unsafe_allow_html=True
                    )
                
                st.caption(f"Last update: {now.strftime('%H:%M:%S UTC')} | Processed in {time.time()-start_time:.2f}s")
            
            if not auto_refresh:
                break
            time.sleep(max(refresh_rate, 10))  # Enforce minimum delay
    
    except Exception as e:
        logger.error(f"App error: {str(e)}")
        st.error("System overload - please reduce refresh rate")

if __name__ == "__main__":
    main()
