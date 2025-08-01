import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# Market Configuration
MARKET_DATA = {
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT"],
    "Commodities": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL"],
    "Indices": ["NIFTY", "BANKNIFTY", "SENSEX"],
    "Forex": ["USDINR", "EURUSD", "GBPUSD"]
}

# Simple Planetary Associations
PLANET_MAPPING = {
    "GOLD": "SUN",
    "SILVER": "MOON",
    "CRUDEOIL": "MARS",
    "RELIANCE": "JUPITER",
    "TATA": "VENUS",
    "HDFC": "MERCURY",
    "NIFTY": "JUPITER",
    "BANKNIFTY": "JUPITER",
    "USD": "VENUS",
    "EUR": "MERCURY"
}

def get_planet(symbol):
    """Simple planet mapping without Swiss Ephemeris"""
    for key, planet in PLANET_MAPPING.items():
        if key in symbol:
            return planet
    return "UNKNOWN"

def generate_signal(symbol, now):
    """Generate demo signals based on time"""
    planet = get_planet(symbol)
    minute = now.minute
    
    if minute < 20:
        signal = "BUY"
    elif minute < 40:
        signal = "HOLD"
    else:
        signal = "SELL"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Signal": signal,
        "Time": now.strftime("%H:%M:%S"),
        "Color": "green" if signal == "BUY" else "red" if signal == "SELL" else "gray"
    }

def main():
    st.set_page_config(
        page_title="Market Astro Signals",
        layout="wide"
    )
    
    st.title("Planetary Market Signals")
    st.info("Demo Mode - Basic planetary associations")
    
    # UI Controls
    market = st.sidebar.selectbox("Select Market", list(MARKET_DATA.keys()))
    refresh = st.sidebar.slider("Refresh Rate (sec)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        now = datetime.now(pytz.utc)
        signals = [generate_signal(symbol, now) for symbol in MARKET_DATA[market]]
        
        with placeholder.container():
            st.subheader(f"{market} Signals - {now.strftime('%H:%M:%S UTC')}")
            
            for signal in signals:
                st.markdown(
                    f"""
                    <div style='
                        border-left: 5px solid {signal['Color']};
                        padding: 8px;
                        margin: 5px 0;
                        border-radius: 5px;
                    '>
                        <strong>{signal['Time']}</strong> | 
                        {signal['Symbol']} | 
                        <span style='color:{signal['Color']};font-weight:bold'>
                            {signal['Signal']} ({signal['Planet']})
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        if not auto_refresh:
            break
        time.sleep(refresh)

if __name__ == "__main__":
    main()
