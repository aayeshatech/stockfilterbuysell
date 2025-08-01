"""
Ultra-Fast Market Astro Signals with Future Symbols and Planetary Transits
"""

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import logging
import yfinance as yf
import ephem
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== ENHANCED CONFIG ==================
MARKET_DATA = {
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT", 
                      "NSE:INFY-FUT", "NSE:ICICIBANK-FUT"],
    "Commodities": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL", "MCX:NATURALGAS"],
    "Crypto Futures": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Global Indices": ["^GSPC", "^NSEI", "^FTSE"]
}

PLANET_MAPPING = {
    "GOLD": "Sun",
    "SILVER": "Moon",
    "CRUDEOIL": "Mars",
    "RELIANCE": "Jupiter",
    "TATA": "Venus",
    "HDFC": "Mercury",
    "INFY": "Saturn",
    "ICICI": "Neptune",
    "BTC": "Uranus",
    "ETH": "Pluto",
    "SOL": "Moon",
    "NATURALGAS": "Venus"
}

# Eye symbol mapping for signals
EYE_SYMBOLS = {
    "BUY": "👁️🟢",
    "SELL": "👁️🔴",
    "HOLD": "👁️⚪"
}

# ================== ENHANCED FUNCTIONS ==================
@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(symbol: str) -> float:
    """Cached price fetch with enhanced error handling"""
    try:
        clean_symbol = symbol.replace("^", "").replace("-FUT", "").replace("-USD", "")
        data = yf.Ticker(clean_symbol).history(period="1d", interval="1m", timeout=5)
        return data["Close"].iloc[-1] if not data.empty else 0.0
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=128)
def get_planet_strength(planet: str, timestamp: float) -> Tuple[float, str]:
    """Enhanced planetary strength with transit info"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        planet_obj.compute(observer)
        
        strength = float(planet_obj.alt / (ephem.pi/2))
        
        # Calculate next significant transit
        next_transit = observer.next_transit(planet_obj)
        transit_time = ephem.localtime(next_transit).strftime("%H:%M UTC")
        
        return strength, transit_time
    except Exception as e:
        logger.warning(f"Planet calc error: {str(e)}")
        return 0.5, "N/A"

def get_planet(symbol: str) -> str:
    """Enhanced symbol-to-planet mapping"""
    for key, planet in PLANET_MAPPING.items():
        if key in symbol.upper():
            return planet
    return "Sun"  # Default to Sun

def get_transit_alert(planet: str, transit_time: str) -> str:
    """Generate transit alert message"""
    alerts = {
        "Sun": "Solar energy peak",
        "Moon": "Lunar phase change",
        "Mercury": "Mercury transit",
        "Venus": "Venus alignment",
        "Mars": "Mars energy surge",
        "Jupiter": "Jupiter expansion",
        "Saturn": "Saturn restriction",
        "Uranus": "Uranus disruption",
        "Neptune": "Neptune intuition",
        "Pluto": "Pluto transformation"
    }
    return f"{alerts.get(planet, 'Planetary transit')} at {transit_time}"

def fetch_all_data(symbols: List[str], now: datetime) -> List[Dict]:
    """Parallel data fetching with enhanced info"""
    timestamp = now.timestamp()
    
    def process_symbol(symbol):
        planet = get_planet(symbol)
        strength, transit_time = get_planet_strength(planet, timestamp)
        price = get_live_price(symbol)
        
        # Enhanced signal logic
        if strength > 0.8: 
            signal = "BUY"
            reason = "Strong planetary alignment"
        elif strength > 0.7: 
            signal = "BUY"
            reason = "Favorable transit"
        elif strength < 0.2:
            signal = "SELL"
            reason = "Challenging aspect"
        elif strength < 0.3:
            signal = "SELL"
            reason = "Negative planetary position"
        else: 
            signal = "HOLD"
            reason = "Neutral planetary influence"
        
        return {
            "Symbol": symbol,
            "Price": f"{price:,.2f}",
            "Signal": f"{EYE_SYMBOLS[signal]} {signal}",
            "Reason": reason,
            "Confidence": f"{strength:.0%}",
            "Planet": planet,
            "Transit": get_transit_alert(planet, transit_time),
            "Color": "green" if "BUY" in signal else "red" if "SELL" in signal else "gray",
            "Strength": strength
        }
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        return sorted(
            list(executor.map(process_symbol, symbols)),
            key=lambda x: x["Strength"], 
            reverse=True
        )

# ================== ENHANCED STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Astro Trading Pro",
        layout="wide",
        page_icon="🔮"
    )
    
    # Enhanced UI
    st.title("🌌 Astro Trading Pro")
    st.caption("Advanced planetary analysis with transit timing")
    
    with st.sidebar:
        st.image("https://i.imgur.com/8Km9tLL.png", width=200)
        market = st.selectbox("Market Segment", list(MARKET_DATA.keys()))
        refresh_rate = st.slider("Refresh Rate (seconds)", 15, 300, 60)
        auto_refresh = st.checkbox("Live Mode", True)
        st.info("""
        **Signal Guide**:  
        👁️🟢 Strong Buy  
        👁️🔴 Strong Sell  
        👁️⚪ Neutral Hold
        """)
    
    placeholder = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            signals = fetch_all_data(MARKET_DATA[market], now)
            
            with placeholder.container():
                # Display planetary transits first
                st.subheader("🌠 Upcoming Planetary Transits")
                transits = {s["Transit"] for s in signals}
                for transit in sorted(transits):
                    st.caption(f"→ {transit}")
                
                # Enhanced signal display
                st.subheader("📈 Market Signals")
                cols = st.columns(3)
                
                for i, signal in enumerate(signals):
                    col = cols[i % 3]
                    with col:
                        st.markdown(
                            f"""<div style='border-left: 5px solid {signal["Color"]}; 
                            padding: 10px; margin: 5px; border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1)'>
                            <h4>{signal["Symbol"]}</h4>
                            <h2>{signal["Signal"]}</h2>
                            <p>Price: <b>{signal["Price"]}</b></p>
                            <p>Planet: <b>{signal["Planet"]}</b></p>
                            <p>Strength: <b>{signal["Confidence"]}</b></p>
                            <small>{signal["Reason"]}</small>
                            </div>""",
                            unsafe_allow_html=True
                        )
                
                st.progress(min(100, int((time.time() - start_time) * 10))
                st.caption(f"Last update: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | "
                          f"Processing time: {time.time()-start_time:.2f}s")
            
            if not auto_refresh:
                break
            time.sleep(refresh_rate)
    
    except Exception as e:
        logger.error(f"App error: {str(e)}")
        st.error(f"System update needed: {str(e)}")

if __name__ == "__main__":
    main()
