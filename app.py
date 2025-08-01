import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import os
from typing import List, Dict, Optional

# Check for Swiss Ephemeris
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    st.warning("Swiss Ephemeris not available - running in demo mode")

# Configuration
EPHE_PATH = './ephe'
if SWISSEPH_AVAILABLE:
    swe.set_ephe_path(EPHE_PATH)

# Market Segment Configuration
MARKET_SEGMENTS = {
    "Equity Futures": [
        "NSE:TRENT1!", "NSE:EICHERMOT1!", "NSE:TVSMOTOR1!", 
        # ... (all your equity futures symbols)
        "NSE:PNBHOUSING1!"
    ],
    "Commodities": [
        "MCX:ALUMINIUM1!", "MCX:COPPER1!", "MCX:CRUDEOIL1!",
        # ... (all commodity symbols)
        "OANDA:XAUUSD"
    ],
    "Indices": [
        "NSE:BANKNIFTY", "NSE:NIFTY", "NSE:CNX100",
        # ... (all index symbols)
        "CAPITALCOM:US500"
    ],
    "Forex": [
        "BITSTAMP:BTCUSD", "CAPITALCOM:DXY",
        # ... (all forex symbols)
        "FX:JPYINR"
    ]
}

# Planetary Rulerships
PLANETARY_RULES = {
    'SUN': ["GOLD", "SILVER", "INDEX"],
    'MOON': ["CRUDEOIL", "NATURALGAS", "CURRENCY"],
    # ... (other planetary rules)
    'KETU': ["PHARMA", "MIDCAP"]
}

def get_planet_position(planet: str, date_utc: datetime) -> tuple:
    """Get planetary position with fallback to demo mode"""
    if not SWISSEPH_AVAILABLE:
        # Demo mode calculation
        deg = (date_utc.hour * 15 + date_utc.minute * 0.25) % 360
        d = int(deg)
        m = int((deg - d) * 60)
        s = int(((deg - d) * 60 - m) * 60)
        return deg, f"{d}°{m}'{s}\"", "Aries"  # Simplified zodiac
    
    # Actual Swiss Ephemeris calculation
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 
                   date_utc.hour + date_utc.minute/60 + date_utc.second/3600)
    
    if planet == 'RAHU':
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    elif planet == 'KETU':
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE)
        pos[0] = (pos[0] + 180) % 360
    else:
        planet_code = getattr(swe, planet)
        pos, _ = swe.calc_ut(jd, planet_code)
    
    deg = pos[0]
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    
    return deg, f"{d}°{m}'{s}\"", "ZodiacSign"  # Implement zodiac lookup

def analyze_transit(symbol: str) -> Optional[Dict]:
    """Analyze transit with fallback support"""
    planet = None
    for p, keywords in PLANETARY_RULES.items():
        if any(kw in symbol.upper() for kw in keywords):
            planet = p
            break
    
    if not planet:
        return None
    
    now = datetime.now(pytz.utc)
    deg, degree_str, zodiac = get_planet_position(planet, now)
    
    # Simplified analysis for demo
    if not SWISSEPH_AVAILABLE:
        signal = "BUY" if deg < 180 else "SELL"
    else:
        # Actual transit analysis
        signal = "BUY" if planet in ['JUPITER', 'VENUS'] else "SELL"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Degree": degree_str,
        "Signal": signal,
        "Time": now.strftime("%H:%M:%S"),
        "Color": "#006400" if signal == "BUY" else "#8B0000"
    }

def main():
    st.set_page_config(
        page_title="Astro Trading Signals",
        layout="wide"
    )
    
    st.title("Planetary Transit Signals")
    
    if not SWISSEPH_AVAILABLE:
        st.warning("Running in demo mode without Swiss Ephemeris")
    
    # Market segment selection
    segment = st.sidebar.selectbox("Select Market", list(MARKET_SEGMENTS.keys()))
    symbols = MARKET_SEGMENTS[segment]
    
    # Analysis
    if st.button("Analyze Transits"):
        results = []
        for symbol in symbols[:50]:  # Limit for demo
            signal = analyze_transit(symbol)
            if signal:
                results.append(signal)
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(
                df.style.apply(
                    lambda x: ["background: #006400; color: white" if v == "BUY" 
                             else "background: #8B0000; color: white" 
                             for v in x],
                    subset=["Signal"]
                )
            )
        else:
            st.warning("No signals generated")

if __name__ == "__main__":
    main()
