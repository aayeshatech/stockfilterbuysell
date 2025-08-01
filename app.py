import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import numpy as np

# Market Configuration
MARKET_SEGMENTS = {
    "Equity Futures": [
        "NSE:TRENT1!", "NSE:EICHERMOT1!", "NSE:TVSMOTOR1!", 
        # ... (all your equity futures)
        "NSE:PNBHOUSING1!"
    ],
    "Commodities": [
        "MCX:ALUMINIUM1!", "MCX:COPPER1!", "MCX:CRUDEOIL1!",
        "MCX:GOLD1!", "MCX:SILVER1!"
    ],
    "Indices": [
        "NSE:BANKNIFTY", "NSE:NIFTY", "NSE:CNX100",
        "NSE:CNX200", "CFI:US100"
    ],
    "Forex": [
        "BTCUSD", "USDINR", "DXY", "EURUSD"
    ]
}

# Planetary Associations
PLANETARY_RULES = {
    'SUN': ["GOLD", "SILVER", "INDEX"],
    'MOON': ["CRUDEOIL", "NATURALGAS", "CURRENCY"],
    'MERCURY': ["BTC", "TECH"],
    'VENUS': ["AUTO", "FMCG"],
    'MARS': ["METAL", "ENERGY"],
    'JUPITER': ["BANK", "FINANCE"],
    'SATURN': ["COMMODITIES", "INDUSTRY"]
}

def get_planet_for_symbol(symbol):
    """Simple planet-symbol association"""
    symbol_key = symbol.split(':')[-1].replace('1!', '') if ':' in symbol else symbol
    for planet, keywords in PLANETARY_RULES.items():
        if any(kw in symbol_key.upper() for kw in keywords):
            return planet
    return None

def generate_demo_signal(symbol, now):
    """Generate plausible demo signals"""
    planet = get_planet_for_symbol(symbol)
    if not planet:
        return None
    
    # Simple time-based pattern for demo
    minute = now.minute
    if minute < 15:
        signal = "BUY"
    elif minute < 45:
        signal = "HOLD"
    else:
        signal = "SELL"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Signal": signal,
        "Time": now.strftime("%H:%M:%S"),
        "Degree": f"{(now.hour % 12)*30 + now.minute*0.5}°",
        "Color": "#006400" if signal == "BUY" else "#8B0000" if signal == "SELL" else "#FFD700"
    }

def main():
    st.set_page_config(
        page_title="Astro Trading Signals",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Planetary Market Signals")
    st.info("Running in demo mode - add Swiss Ephemeris for precise calculations")
    
    # UI Controls
    segment = st.sidebar.selectbox("Market Segment", list(MARKET_SEGMENTS.keys()))
    refresh_rate = st.sidebar.slider("Refresh (seconds)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        now = datetime.now(pytz.utc)
        signals = []
        
        for symbol in MARKET_SEGMENTS[segment][:50]:  # Limit for performance
            signal = generate_demo_signal(symbol, now)
            if signal:
                signals.append(signal)
        
        with placeholder.container():
            st.subheader(f"{segment} Signals - {now.strftime('%H:%M:%S UTC')}")
            
            if signals:
                # Summary Stats
                col1, col2, col3 = st.columns(3)
                col1.metric("Buy Signals", len([s for s in signals if s['Signal'] == "BUY"]))
                col2.metric("Sell Signals", len([s for s in signals if s['Signal'] == "SELL"]))
                col3.metric("Total Signals", len(signals))
                
                # Display Signals
                for signal in signals:
                    st.markdown(
                        f"""
                        <div style='
                            border-left: 5px solid {signal['Color']};
                            padding: 10px;
                            margin: 5px 0;
                            background-color: #f8f9fa;
                            border-radius: 5px;
                        '>
                            <strong>{signal['Time']}</strong> | 
                            {signal['Symbol']} | 
                            <span style='color:{signal['Color']};font-weight:bold'>{signal['Signal']}</span> | 
                            {signal['Planet']} {signal['Degree']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("No signals generated for selected segment")
        
        if not auto_refresh:
            break
            
        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()
