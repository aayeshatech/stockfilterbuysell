import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# Enhanced Market Configuration
MARKET_CATEGORIES = {
    "Commodity": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL", "MCX:NATURALGAS"],
    "Forex": ["BTCUSD", "USDINR", "DXY", "EURUSD", "GBPUSD"],
    "Global Indices": ["DOWJONES", "SNP500", "NASDAQ", "FTSE100", "NIKKEI225"],
    "Sectors": ["NIFTYMIDCAP", "NIFTYPSUBANK", "NIFTYPHARMA", "NIFTYAUTO", "NIFTYFMCG", "CNX100", "CNX500"],
    "Equity Futures": ["NSE:RELIANCE-FUT", "NSE:TATASTEEL-FUT", "NSE:HDFCBANK-FUT"]
}

# Planetary Rulerships (Expanded)
PLANETARY_RULES = {
    'SUN': ["GOLD", "SILVER", "INDEX"],
    'MOON': ["CRUDEOIL", "NATURALGAS", "CURRENCY"],
    'MERCURY': ["BTC", "TECH", "PHARMA"],
    'VENUS': ["LUXURY", "AUTO", "FMCG"],
    'MARS': ["METAL", "ENERGY", "DEFENSE"],
    'JUPITER': ["BANK", "FINANCE", "USD"],
    'SATURN': ["PSU", "COMMODITIES", "INDUSTRY"],
    'RAHU': ["SPECULATIVE", "CRYPTO"],
    'KETU': ["PHARMA", "MIDCAP"]
}

# Zodiac Signs
ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_planet_position(planet, date_utc):
    """Calculate planet position with degrees"""
    # In production, replace with actual Swiss Ephemeris calculations
    hour_deg = (date_utc.hour % 12) * 30  # 30° per zodiac sign
    minute_deg = date_utc.minute * 0.5    # 0.5° per minute
    deg = (hour_deg + minute_deg) % 360
    
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    
    sign_idx = int(deg / 30)
    zodiac = f"{ZODIAC_SIGNS[sign_idx]} {deg%30:.1f}°"
    
    return deg, f"{d}°{m}'{s}\"", zodiac

def analyze_transit(symbol):
    """Generate trading signal based on planetary position"""
    planet = None
    for p, keywords in PLANETARY_RULES.items():
        if any(kw in symbol.upper() for kw in keywords):
            planet = p
            break
    
    if not planet:
        return None
    
    now = datetime.now(pytz.utc)
    deg, degree_str, zodiac = get_planet_position(planet, now)
    
    # Simple aspect analysis
    if planet in ['JUPITER', 'VENUS', 'MOON']:
        signal = "BUY" if deg < 180 else "HOLD"
    elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
        signal = "SELL" if deg > 90 else "HOLD"
    else:
        signal = "HOLD"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Degree": degree_str,
        "Zodiac": zodiac,
        "Signal": signal,
        "Time": now.strftime("%H:%M:%S"),
        "Color": "#006400" if signal == "BUY" else "#8B0000" if signal == "SELL" else "#FFD700"
    }

def main():
    st.set_page_config(
        page_title="Advanced Astro Trader",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌌 Planetary Transit Trading Signals")
    st.markdown("""
    <style>
    .signal-buy { background-color: #00640040; padding: 5px; border-radius: 5px; }
    .signal-sell { background-color: #8B000040; padding: 5px; border-radius: 5px; }
    .signal-hold { background-color: #FFD70040; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Market Selection
    selected_market = st.sidebar.selectbox(
        "Select Market Segment",
        list(MARKET_CATEGORIES.keys())
    )
    
    # Symbol Selection
    selected_symbols = st.sidebar.multiselect(
        "Select Symbols",
        MARKET_CATEGORIES[selected_market],
        default=MARKET_CATEGORIES[selected_market][:2]
    )
    
    # Refresh Controls
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        signals = []
        for symbol in selected_symbols:
            signal = analyze_transit(symbol)
            if signal:
                signals.append(signal)
        
        with placeholder.container():
            # Market Header
            st.header(f"{selected_market} Signals")
            
            # Create DataFrame
            if signals:
                df = pd.DataFrame(signals)
                
                # Display with colored signals
                for _, row in df.iterrows():
                    st.markdown(
                        f"""
                        <div class="signal-{row['Signal'].lower()}">
                            <strong>{row['Time']}</strong> | 
                            {row['Symbol']} | 
                            <strong>{row['Planet']}</strong> in {row['Zodiac']} | 
                            <span style='color:{row['Color']};font-weight:bold'>{row['Signal']}</span> | 
                            {row['Degree']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Summary Stats
                cols = st.columns(3)
                cols[0].metric("Buy Signals", len(df[df['Signal'] == "BUY"]))
                cols[1].metric("Sell Signals", len(df[df['Signal'] == "SELL"]))
                cols[2].metric("Active Signals", len(df))
            else:
                st.warning("No signals generated for selected symbols")
        
        if not auto_refresh:
            break
            
        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()
