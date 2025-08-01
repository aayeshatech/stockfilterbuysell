import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import os
import swisseph as swe

# Configure Swiss Ephemeris with your ephemeris files
EPHE_PATH = r"C:\Users\a\Downloads\swisseph-master (1)\swisseph-master\ephe"
swe.set_ephe_path(EPHE_PATH)

# Market Configuration
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
    """Get precise planetary position using Swiss Ephemeris"""
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 
                   date_utc.hour + date_utc.minute/60 + date_utc.second/3600)
    
    if planet == 'RAHU':
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    elif planet == 'KETU':
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        pos[0] = (pos[0] + 180) % 360
    else:
        try:
            planet_code = getattr(swe, planet)
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, planet_code, flags)
        except AttributeError:
            raise ValueError(f"Unknown planet: {planet}")
    
    deg = pos[0]
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    
    sign_idx = int(deg / 30)
    zodiac = f"{ZODIAC_SIGNS[sign_idx]} {deg%30:.1f}°"
    
    return deg, f"{d}°{m}'{s}\"", zodiac

def analyze_transit(symbol):
    """Generate trading signal based on precise planetary transits"""
    planet = None
    for p, keywords in PLANETARY_RULES.items():
        if any(kw in symbol.upper() for kw in keywords):
            planet = p
            break
    
    if not planet:
        return None
    
    now = datetime.now(pytz.utc)
    deg, degree_str, zodiac = get_planet_position(planet, now)
    
    # Advanced aspect analysis
    natal_pos = deg  # Replace with actual natal positions for each symbol
    aspect_diff = abs((deg - natal_pos) % 360)
    
    if planet in ['JUPITER', 'VENUS', 'MOON']:
        if aspect_diff <= 3:  # Conjunction
            signal = "STRONG BUY"
            strength = "High"
        elif 60 <= aspect_diff <= 65:  # Sextile
            signal = "BUY"
            strength = "Medium"
        elif 120 <= aspect_diff <= 125:  # Trine
            signal = "BUY"
            strength = "High"
        else:
            signal = "NEUTRAL"
            strength = "Low"
    elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
        if aspect_diff <= 3:  # Conjunction
            signal = "STRONG SELL"
            strength = "High"
        elif 90 <= aspect_diff <= 95:  # Square
            signal = "SELL"
            strength = "Medium"
        elif 180 <= aspect_diff <= 185:  # Opposition
            signal = "SELL"
            strength = "High"
        else:
            signal = "NEUTRAL"
            strength = "Low"
    else:
        signal = "HOLD"
        strength = "Low"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Degree": degree_str,
        "Zodiac": zodiac,
        "Signal": signal,
        "Strength": strength,
        "Time": now.strftime("%H:%M:%S"),
        "Color": "#006400" if "BUY" in signal else "#8B0000" if "SELL" in signal else "#FFD700"
    }

def main():
    st.set_page_config(
        page_title="Professional Astro Trader",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("♈️ Live Planetary Transit Trading Signals")
    st.markdown(f"Using ephemeris files from: `{EPHE_PATH}`")
    
    # Market Selection
    selected_market = st.sidebar.selectbox(
        "Market Segment",
        list(MARKET_CATEGORIES.keys())
    )
    
    # Symbol Selection
    selected_symbols = st.sidebar.multiselect(
        "Symbols",
        MARKET_CATEGORIES[selected_market],
        default=MARKET_CATEGORIES[selected_market][:2]
    )
    
    # Analysis Controls
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Live Mode", True)
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        signals = []
        for symbol in selected_symbols:
            try:
                signal = analyze_transit(symbol)
                if signal:
                    signals.append(signal)
            except Exception as e:
                st.error(f"Error analyzing {symbol}: {str(e)}")
        
        with placeholder.container():
            # Market Header
            st.subheader(f"{selected_market} - Planetary Transit Signals")
            
            if signals:
                # Create DataFrame
                df = pd.DataFrame(signals)
                
                # Display each signal with styling
                for _, row in df.iterrows():
                    st.markdown(
                        f"""
                        <div style='
                            border-left: 5px solid {row['Color']};
                            padding: 10px;
                            margin: 5px 0;
                            background-color: #f8f9fa;
                            border-radius: 5px;
                        '>
                            <strong>{row['Time']}</strong> | 
                            <strong>{row['Symbol']}</strong> | 
                            <span style='color:{row['Color']};font-weight:bold'>{row['Signal']}</span> | 
                            {row['Planet']} in {row['Zodiac']} ({row['Degree']})<br>
                            <small>Strength: {row['Strength']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Summary Statistics
                col1, col2, col3 = st.columns(3)
                col1.metric("Strong Buy Signals", 
                          len(df[df['Signal'] == "STRONG BUY"]),
                          delta_color="off")
                col2.metric("Strong Sell Signals", 
                          len(df[df['Signal'] == "STRONG SELL"]),
                          delta_color="off")
                col3.metric("Total Active Signals", 
                          len(df),
                          delta_color="off")
            else:
                st.warning("No planetary transits detected for selected symbols")
        
        if not auto_refresh:
            break
            
        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()
