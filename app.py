"""
Market Astro Signals
Generates trading signals based on planetary associations and time-based logic.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time
import logging

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
MARKET_DATA = {
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT"],
    "Commodities": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL"],
    "Indices": ["NIFTY", "BANKNIFTY", "SENSEX"],
    "Forex": ["USDINR", "EURUSD", "GBPUSD"]
}

PLANET_MAPPING = {
    "GOLD": "SUN", "SILVER": "MOON", "CRUDEOIL": "MARS",
    "RELIANCE": "JUPITER", "TATA": "VENUS", "HDFC": "MERCURY",
    "NIFTY": "JUPITER", "BANKNIFTY": "JUPITER", "SENSEX": "SUN",
    "USD": "VENUS", "EUR": "MERCURY", "GBP": "JUPITER", "INR": "VENUS"
}

# --- Functions ---
def get_planet(symbol: str) -> str:
    """Map a trading symbol to its associated planet."""
    for key, planet in PLANET_MAPPING.items():
        if key in symbol:
            return planet
    return "UNKNOWN"

def generate_signal(symbol: str, now: datetime) -> Dict[str, str]:
    """Generate a mock signal based on current minute."""
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

# --- Main App ---
def main():
    st.set_page_config(
        page_title="Market Astro Signals",
        layout="wide",
        page_icon="✨"
    )

    st.title("Planetary Market Signals")
    st.info("Note: Signals are generated based on mock planetary logic.")

    # Sidebar Controls
    market = st.sidebar.selectbox("Select Market", list(MARKET_DATA.keys()))
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Auto Refresh", True)

    # Main Display
    placeholder = st.empty()

    try:
        while True:
            now = datetime.now(pytz.utc)
            signals = [generate_signal(symbol, now) for symbol in MARKET_DATA[market]]
            signals_df = pd.DataFrame(signals)

            with placeholder.container():
                st.subheader(f"{market} Signals - {now.strftime('%H:%M:%S UTC')}")
                st.dataframe(
                    signals_df.style.apply(
                        lambda x: [f"color: {x['Color']}" if x.name == 'Signal' else "" for _ in x],
                        axis=1
                    ),
                    hide_index=True
                )

            if not auto_refresh:
                break
            time.sleep(refresh_rate)

    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
