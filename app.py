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
    "SENSEX": "SUN",
    "USD": "VENUS",
    "EUR": "MERCURY",
    "GBP": "JUPITER",
    "INR": "VENUS"
}

def get_planet(symbol):
    for key, planet in PLANET_MAPPING.items():
        if key in symbol:
            return planet
    return "UNKNOWN"

def generate_signal(symbol, now):
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
    
    try:
        now = datetime.now(pytz.utc)
        signals = [generate_signal(symbol, now) for symbol in MARKET_DATA[market]]
        
        with placeholder.container():
            st.subheader(f"{market} Signals - {now.strftime('%H:%M:%S UTC')}")
            signals_df = pd.DataFrame(signals)
            st.dataframe(signals_df.style.apply(lambda x: [f"color: {x['Color']}" if x.name == 'Signal' else "" for _ in x], axis=1))
        
        if auto_refresh:
            time.sleep(refresh)
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Error generating signals: {e}")

if __name__ == "__main__":
    main()
