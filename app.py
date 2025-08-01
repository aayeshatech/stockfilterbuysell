"""
Market Astro Signals Pro - Advanced trading signals with planetary analysis
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import ephem
import pytz
import time
import logging
from datetime import datetime
from typing import Dict, List
from telegram import Bot  # Remove if not using Telegram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================
MARKET_DATA = {
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT"],
    "Commodities": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL"],
    "Indices": ["NIFTY", "BANKNIFTY", "SENSEX"],
    "Forex": ["USDINR", "EURUSD", "GBPUSD"]
}

PLANET_MAPPING = {
    "GOLD": "Sun",
    "SILVER": "Moon",
    "CRUDEOIL": "Mars",
    "RELIANCE": "Jupiter",
    "TATA": "Venus",
    "HDFC": "Mercury",
    "NIFTY": "Jupiter",
    "BANKNIFTY": "Jupiter",
    "SENSEX": "Sun",
    "USD": "Venus",
    "EUR": "Mercury",
    "GBP": "Jupiter",
    "INR": "Venus"
}

# ================== CORE FUNCTIONS ==================
def get_planet(symbol: str) -> str:
    """Map trading symbol to astrological planet"""
    for key, planet in PLANET_MAPPING.items():
        if key in symbol:
            return planet
    return "Unknown"

def get_planet_strength(planet: str, now: datetime) -> float:
    """Calculate planetary influence (0-1) using ephemeris"""
    try:
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        planet_obj.compute(observer)
        return float(planet_obj.alt / (ephem.pi/2))  # Normalized altitude
    except Exception as e:
        logger.warning(f"Planet calc error: {e}")
        return 0.5  # Default neutral strength

def get_live_price(symbol: str) -> float:
    """Fetch real-time market price"""
    try:
        clean_symbol = symbol.split(":")[-1].split("-")[0]
        return yf.Ticker(clean_symbol).history(period="1d")["Close"].iloc[-1]
    except Exception as e:
        logger.error(f"Price fetch failed: {e}")
        return 0.0

def generate_signal(symbol: str, now: datetime) -> Dict[str, str]:
    """Generate enhanced trading signal"""
    planet = get_planet(symbol)
    strength = get_planet_strength(planet, now)
    price = get_live_price(symbol)
    
    # Signal logic matrix
    if strength > 0.7 and now.minute < 30:
        signal = "STRONG BUY"
    elif strength > 0.6:
        signal = "BUY"
    elif strength < 0.3 and now.minute > 30:
        signal = "STRONG SELL"
    elif strength < 0.4:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        "Symbol": symbol,
        "Price": f"{price:,.2f}",
        "Signal": signal,
        "Confidence": f"{strength:.0%}",
        "Planet": planet,
        "Time": now.strftime("%H:%M:%S"),
        "Color": ("green" if "BUY" in signal else 
                 "red" if "SELL" in signal else 
                 "gray")
    }

# ================== VISUALIZATION ==================
def plot_performance(symbol: str):
    """Generate interactive price chart"""
    try:
        clean_symbol = symbol.split(":")[-1].split("-")[0]
        data = yf.download(clean_symbol, period="1mo")
        fig = go.Figure(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        fig.update_layout(
            title=f"{symbol} 30-Day Performance",
            xaxis_rangeslider_visible=False
        )
        return fig
    except Exception as e:
        logger.error(f"Chart error: {e}")
        return None

# ================== MAIN APP ==================
def main():
    st.set_page_config(
        page_title="Market Astro Signals Pro",
        layout="wide",
        page_icon="✨"
    )
    
    # Header
    st.title("Planetary Market Signals Pro")
    st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">Real-time signals combining astrological patterns and market data</p>', 
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Controls")
        market = st.selectbox("Select Market", list(MARKET_DATA.keys()))
        refresh_rate = st.slider("Refresh (sec)", 5, 60, 15)
        auto_refresh = st.checkbox("Auto Refresh", True)
        if st.button("🔄 Manual Refresh"):
            st.experimental_rerun()
    
    # Main Display
    placeholder = st.empty()
    
    try:
        while True:
            now = datetime.now(pytz.utc)
            signals = [generate_signal(symbol, now) for symbol in MARKET_DATA[market]]
            signals_df = pd.DataFrame(signals)
            
            with placeholder.container():
                # Signals Table
                st.subheader(f"{market} Signals - {now.strftime('%H:%M:%S UTC')}")
                st.dataframe(
                    signals_df.style.apply(
                        lambda x: [f"background-color: {x['Color']}; color: white" 
                                 if x.name == 'Signal' else "" for _ in x],
                        axis=1
                    ),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Charts
                for symbol in MARKET_DATA[market]:
                    with st.expander(f"📊 {symbol} Charts"):
                        fig = plot_performance(symbol)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Chart data unavailable")
            
            if not auto_refresh:
                break
            time.sleep(refresh_rate)
            
    except Exception as e:
        logger.exception("App crashed")
        st.error(f"System error: {str(e)}")

if __name__ == "__main__":
    main()
