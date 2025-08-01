import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import swisseph as swe
from typing import List, Dict, Optional

# Configure Swiss Ephemeris
EPHE_PATH = r"C:\Users\a\Downloads\swisseph-master (1)\swisseph-master\ephe"
swe.set_ephe_path(EPHE_PATH)

# Market Segment Configuration
MARKET_SEGMENTS = {
    "Equity Futures": [
        "NSE:TRENT1!", "NSE:EICHERMOT1!", "NSE:TVSMOTOR1!", "NSE:AMBUJACEM1!", 
        "NSE:MARICO1!", "NSE:DABUR1!", "NSE:ITC1!", "NSE:ASIANPAINT1!",
        # ... (all your equity futures symbols)
        "NSE:PNBHOUSING1!"
    ],
    "Commodities": [
        "MCX:ALUMINIUM1!", "MCX:COPPER1!", "MCX:CRUDEOIL1!", "MCX:GOLD1!",
        "MCX:SILVER1!", "COMEX:GC1!", "FX:USOIL", "OANDA:XAUUSD",
        "OANDA:XAGUSD", "BIST:XAGUSD1!", "FX:XAUUSD", "OANDA:SUGARUSD"
    ],
    "Indices": [
        "NSE:BANKNIFTY", "NSE:NIFTY", "NSE:CNX100", "NSE:CNX200",
        "NSE:CNXAUTO", "NSE:CNXCOMMODITIES", "NSE:CNXCONSUMPTION",
        # ... (all your index symbols)
        "CFI:US100", "TVC:US10Y", "FX:US30", "CAPITALCOM:US500"
    ],
    "Forex": [
        "BITSTAMP:BTCUSD", "CAPITALCOM:DXY", "COINBASE:ETHUSD", 
        "BITSTAMP:ETHUSD", "FX_IDC:USDINR", "FX:UKOIL", "FX:EURUSD",
        "FX:GBPUSD", "FX:JPYINR"
    ]
}

# Enhanced Planetary Rulerships
PLANETARY_RULES = {
    'SUN': ["GOLD", "SILVER", "INDEX", "NIFTY", "BANKNIFTY"],
    'MOON': ["CRUDEOIL", "NATURALGAS", "CURRENCY", "USDINR", "DXY"],
    'MERCURY': ["BTC", "ETH", "TECH", "PHARMA", "IT"],
    'VENUS': ["LUXURY", "AUTO", "FMCG", "CONSUMPTION"],
    'MARS': ["METAL", "ALUMINIUM", "COPPER", "STEEL", "ENERGY"],
    'JUPITER': ["BANK", "FINANCE", "FINNIFTY", "INSURANCE"],
    'SATURN': ["INFRA", "COMMODITIES", "OIL", "GAS", "PSE"],
    'RAHU': ["SPECULATIVE", "CRYPTO", "VIX"],
    'KETU': ["PHARMA", "MIDCAP", "SMALLCAP"]
}

# Zodiac Signs
ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_planet_position(planet: str, date_utc: datetime) -> tuple:
    """Get precise planetary position using Swiss Ephemeris"""
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
    
    sign_idx = int(deg / 30)
    zodiac = f"{ZODIAC_SIGNS[sign_idx]} {deg%30:.1f}°"
    
    return deg, f"{d}°{m}'{s}\"", zodiac

def get_planet_for_symbol(symbol: str) -> Optional[str]:
    """Determine planetary ruler for symbol"""
    symbol_key = symbol.split(':')[-1].replace('1!', '') if ':' in symbol else symbol
    for planet, keywords in PLANETARY_RULES.items():
        if any(kw in symbol_key.upper() for kw in keywords):
            return planet
    return None

def analyze_transit(symbol: str) -> Optional[Dict]:
    """Generate trading signal based on precise planetary transits"""
    planet = get_planet_for_symbol(symbol)
    if not planet:
        return None
    
    now = datetime.now(pytz.utc)
    deg, degree_str, zodiac = get_planet_position(planet, now)
    
    # Aspect analysis (simplified)
    natal_pos = deg  # Replace with actual natal positions
    aspect_diff = abs((deg - natal_pos) % 360)
    
    if planet in ['JUPITER', 'VENUS', 'MOON']:
        if aspect_diff <= 3:  # Conjunction
            signal = "STRONG BUY"
        elif 60 <= aspect_diff <= 65:  # Sextile
            signal = "BUY"
        elif 120 <= aspect_diff <= 125:  # Trine
            signal = "BUY"
        else:
            signal = "NEUTRAL"
    elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
        if aspect_diff <= 3:  # Conjunction
            signal = "STRONG SELL"
        elif 90 <= aspect_diff <= 95:  # Square
            signal = "SELL"
        elif 180 <= aspect_diff <= 185:  # Opposition
            signal = "SELL"
        else:
            signal = "NEUTRAL"
    else:
        signal = "HOLD"
    
    return {
        "Symbol": symbol,
        "Planet": planet,
        "Degree": degree_str,
        "Zodiac": zodiac,
        "Signal": signal,
        "Time": now.strftime("%H:%M:%S"),
        "Color": "#006400" if "BUY" in signal else "#8B0000" if "SELL" in signal else "#FFD700"
    }

def main():
    st.set_page_config(
        page_title="Advanced Market Astro Trader",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌐 Multi-Segment Planetary Transit Signals")
    st.markdown(f"Using ephemeris files from: `{EPHE_PATH}`")
    
    # Segment Selection
    selected_segment = st.sidebar.selectbox(
        "Market Segment",
        list(MARKET_SEGMENTS.keys())
    )
    
    # Symbol Filter
    search_term = st.sidebar.text_input("Filter Symbols", "")
    
    # Get filtered symbols
    symbols = [s for s in MARKET_SEGMENTS[selected_segment] 
              if search_term.upper() in s.upper()]
    
    # Analysis Controls
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 15)
    auto_refresh = st.sidebar.checkbox("Live Mode", True)
    show_details = st.sidebar.checkbox("Show Transit Details", True)
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        signals = []
        for symbol in symbols[:50]:  # Limit to 50 symbols for performance
            try:
                signal = analyze_transit(symbol)
                if signal:
                    signals.append(signal)
            except Exception as e:
                st.error(f"Error analyzing {symbol}: {str(e)}")
        
        with placeholder.container():
            st.header(f"{selected_segment} - Planetary Signals")
            
            if signals:
                # Summary Stats
                buy_signals = len([s for s in signals if "BUY" in s["Signal"]])
                sell_signals = len([s for s in signals if "SELL" in s["Signal"]])
                
                cols = st.columns(3)
                cols[0].metric("Total Symbols", len(signals))
                cols[1].metric("Buy Signals", buy_signals)
                cols[2].metric("Sell Signals", sell_signals)
                
                # Display signals
                for signal in signals:
                    with st.expander(f"{signal['Symbol']} - {signal['Signal']}", expanded=False):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**Planet:** {signal['Planet']}")
                            st.markdown(f"**Position:** {signal['Zodiac']}")
                            st.markdown(f"**Degree:** {signal['Degree']}")
                        with col2:
                            st.markdown(f"**Time:** {signal['Time']}")
                            if show_details:
                                st.markdown(f"**Analysis:** {signal['Planet']} in {signal['Zodiac']} forming "
                                           f"a {signal['Signal']} configuration")
                
                # Zodiac Wheel Visualization
                if selected_segment in ["Commodities", "Indices"]:
                    try:
                        import plotly.graph_objects as go
                        
                        fig = go.Figure()
                        for signal in signals:
                            if signal["Planet"] in ["SUN", "MOON", "MERCURY", "VENUS", 
                                                  "MARS", "JUPITER", "SATURN"]:
                                fig.add_trace(go.Scatterpolar(
                                    r=[1],
                                    theta=[float(signal['Degree'].split('°')[0])],
                                    mode='markers+text',
                                    marker=dict(
                                        size=20,
                                        color=signal['Color'],
                                        symbol='circle'
                                    ),
                                    text=[signal['Planet']],
                                    name=signal['Symbol']
                                ))
                        
                        fig.update_layout(
                            polar=dict(
                                angularaxis=dict(
                                    tickvals=list(range(0, 360, 30)),
                                    ticktext=ZODIAC_SIGNS,
                                    direction='clockwise'
                                )
                            ),
                            showlegend=False,
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except ImportError:
                        st.warning("Plotly not available for advanced charts")
            else:
                st.warning("No signals generated for selected filters")
        
        if not auto_refresh:
            break
            
        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()
