import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# Safe import with version checking
def safe_import(module_name, min_version=None):
    try:
        module = __import__(module_name)
        if min_version:
            from pkg_resources import parse_version
            if parse_version(module.__version__) < parse_version(min_version):
                st.warning(f"{module_name} version {module.__version__} is below recommended {min_version}")
        return module
    except ImportError:
        st.warning(f"{module_name} not available - some features disabled")
        return None

# Import with fallbacks
plotly = safe_import("plotly", "5.0.0")
swe = safe_import("swisseph")

# Configuration
CONFIG = {
    "EPHE_PATH": "./ephe",
    "REFRESH_RATE": 15  # seconds
}

if swe:
    try:
        swe.set_ephe_path(CONFIG["EPHE_PATH"])
    except Exception as e:
        st.error(f"Swiss Ephemeris init error: {e}")

# Market data
MARKET_DATA = {
    "Equity": ["NSE:RELIANCE", "NSE:TCS", "NSE:HDFCBANK"],
    "Commodity": ["MCX:GOLD", "MCX:SILVER"],
    "Index": ["NSE:NIFTY", "NSE:BANKNIFTY"],
    "Forex": ["USDINR", "EURINR"]
}

def get_planet_position(symbol, dt):
    """Safe position calculation with fallback"""
    if not swe:
        return 0, "0°0'0\"", "Aries 0°"  # Demo values
    
    # Actual implementation would use Swiss Ephemeris here
    return 15.5, "15°30'0\"", "Aries 15.5°"

def main():
    st.set_page_config(
        page_title="Astro Trader",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Planetary Transit Signals")
    
    # UI Controls
    with st.sidebar:
        st.header("Configuration")
        market = st.selectbox("Market", list(MARKET_DATA.keys()))
        symbols = st.multiselect(
            "Symbols", 
            MARKET_DATA[market],
            default=MARKET_DATA[market][:2]
        )
        refresh_rate = st.slider("Refresh (sec)", 5, 60, CONFIG["REFRESH_RATE"])
    
    # Display Area
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # Generate sample data
            data = []
            for symbol in symbols:
                pos, deg, zodiac = get_planet_position(symbol, datetime.now())
                signal = "BUY" if pos < 180 else "SELL"
                data.append({
                    "Symbol": symbol,
                    "Signal": signal,
                    "Degree": deg,
                    "Zodiac": zodiac,
                    "Time": datetime.now().strftime("%H:%M:%S")
                })
            
            # Display as table
            df = pd.DataFrame(data)
            st.dataframe(
                df.style.applymap(
                    lambda x: "background-color: #006400; color: white" if x == "BUY" else
                             "background-color: #8B0000; color: white",
                    subset=["Signal"]
                ),
                use_container_width=True
            )
            
            # Optional Plotly chart
            if plotly:
                fig = plotly.graph_objects.Figure()
                fig.add_trace(plotly.graph_objects.Table(
                    header=dict(values=df.columns),
                    cells=dict(values=[df[col] for col in df.columns])
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()
