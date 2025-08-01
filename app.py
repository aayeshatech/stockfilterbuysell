import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Swiss Ephemeris setup
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

# Market categories with example symbols
MARKET_CATEGORIES = {
    "Equity": ["RELIANCE", "TATASTEEL", "HDFCBANK", "INFY", "TCS"],
    "Commodity": ["GOLD", "SILVER", "CRUDEOIL", "COPPER", "NATURALGAS"],
    "Index": ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX", "NIFTYMIDCAP"],
    "Forex": ["USDINR", "EURINR", "GBPINR", "JPYINR", "AUDINR"]
}

# Planetary rulerships
PLANETARY_RULES = {
    'SUN': ["GOLD", "SILVER", "INDEX"],
    'MOON': ["CURRENCY", "FMCG", "BANK"],
    'MERCURY': ["IT", "TECH", "PHARMA"],
    'VENUS': ["LUXURY", "AUTO", "REALTY"],
    'MARS': ["METAL", "DEFENSE", "ENERGY"],
    'JUPITER': ["BANK", "FINANCE", "EDUCATION"],
    'SATURN': ["INFRA", "COMMODITIES", "STEEL"],
    'RAHU': ["CRYPTO", "SPECULATIVE"],
    'KETU': ["PHARMA", "PSU"]
}

def get_planet_position(planet, date_utc):
    """Get planet's longitude with degree, minute, second"""
    if not SWISSEPH_AVAILABLE:
        deg = (date_utc.hour * 15 + date_utc.minute * 0.25) % 360
        return deg, int(deg), int((deg % 1) * 60), int(((deg % 1) * 60 % 1) * 60)
    
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 
                   date_utc.hour + date_utc.minute/60 + date_utc.second/3600)
    try:
        planet_code = getattr(swe, planet)
    except AttributeError:
        if planet == 'RAHU':
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        elif planet == 'KETU':
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
            pos[0] = (pos[0] + 180) % 360
        else:
            raise ValueError(f"Unknown planet: {planet}")
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        pos, _ = swe.calc_ut(jd, planet_code, flags)
    
    deg = pos[0]
    return deg, int(deg), int((deg % 1) * 60), int(((deg % 1) * 60 % 1) * 60)

def get_planet_for_symbol(symbol):
    """Determine planetary ruler for symbol"""
    symbol_upper = symbol.split(':')[-1] if ':' in symbol else symbol
    for planet, keywords in PLANETARY_RULES.items():
        for keyword in keywords:
            if keyword in symbol_upper:
                return planet
    return None

def analyze_transits(symbols):
    """Generate trading signals with transit details"""
    now_utc = datetime.now(pytz.utc)
    alerts = []
    
    for symbol in symbols:
        planet = get_planet_for_symbol(symbol)
        if not planet:
            continue
            
        try:
            deg, d, m, s = get_planet_position(planet, now_utc)
            natal_pos = deg  # Replace with actual natal positions
            
            # Aspect analysis
            aspect_diff = abs((deg - natal_pos) % 360)
            if aspect_diff <= 3:  # Conjunction
                if planet in ['JUPITER', 'VENUS', 'MOON']:
                    signal = 'BUY'
                    reason = f"{planet} conjunction ({d}°{m}'{s}\")"
                elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
                    signal = 'SELL'
                    reason = f"{planet} conjunction ({d}°{m}'{s}\")"
                else:
                    signal = 'HOLD'
                    reason = f"Solar influence ({d}°{m}'{s}\")"
                
                alerts.append({
                    'Symbol': symbol,
                    'Market': get_market_type(symbol),
                    'Signal': signal,
                    'Planet': planet,
                    'Degree': f"{d}°{m}'{s}\"",
                    'Position': deg,
                    'Time': now_utc,
                    'Reason': reason
                })
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return alerts

def get_market_type(symbol):
    """Categorize symbol by market type"""
    symbol_upper = symbol.upper()
    if any(m in symbol_upper for m in ['NSE:', 'BSE:']):
        return "Equity"
    elif 'MCX:' in symbol_upper:
        return "Commodity"
    elif any(m in symbol_upper for m in ['NIFTY', 'SENSEX', 'INDEX']):
        return "Index"
    elif any(m in symbol_upper for m in ['USD', 'EUR', 'GBP', 'JPY', 'INR']):
        return "Forex"
    return "Other"

def display_market_dashboard(alerts):
    """Create tabs for each market type with detailed transit info"""
    if not alerts:
        st.info("No active signals currently")
        return
    
    df = pd.DataFrame(alerts)
    market_tabs = st.tabs(["All Markets"] + list(MARKET_CATEGORIES.keys()))
    
    with market_tabs[0]:  # All Markets
        st.subheader("All Market Signals")
        display_signals_table(df)
    
    for i, market in enumerate(MARKET_CATEGORIES.keys(), 1):
        with market_tabs[i]:
            st.subheader(f"{market} Signals")
            market_df = df[df['Market'] == market]
            if not market_df.empty:
                display_signals_table(market_df)
                display_zodiac_chart(market_df)
            else:
                st.info(f"No active signals in {market}")

def display_signals_table(df):
    """Display signals in a color-coded table"""
    st.dataframe(
        df.style.applymap(
            lambda x: 'background-color: #006400; color: white' if x == 'BUY' else
                     'background-color: #8B0000; color: white' if x == 'SELL' else
                     'background-color: #FFD700; color: black',
            subset=['Signal']
        ).format({
            'Time': lambda x: x.strftime('%H:%M:%S')
        }),
        column_order=['Time', 'Symbol', 'Signal', 'Planet', 'Degree', 'Reason'],
        use_container_width=True,
        height=min(400, 35 * len(df) + 35)
    )

def display_zodiac_chart(df):
    """Show zodiac wheel with planet positions"""
    zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                   'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    fig = go.Figure()
    
    for _, row in df.iterrows():
        deg = row['Position']
        sign_idx = int(deg / 30)
        sign_pos = deg % 30
        sign = zodiac_signs[sign_idx]
        
        fig.add_trace(go.Scatterpolar(
            r=[1],
            theta=[sign_pos],
            mode='markers+text',
            marker=dict(
                size=20,
                color='darkgreen' if row['Signal'] == 'BUY' else 'crimson',
                symbol='hexagram' if row['Planet'] in ['RAHU', 'KETU'] else 'circle'
            ),
            text=f"{row['Planet']}<br>{row['Symbol']}",
            textposition='middle center',
            name=f"{row['Symbol']} - {row['Signal']}",
            hoverinfo='text',
            hovertext=f"{row['Symbol']}<br>{row['Planet']} {sign} {row['Degree']}<br>{row['Reason']}"
        ))
    
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickvals=list(range(0, 360, 30)),
                ticktext=zodiac_signs,
                direction='clockwise',
                rotation=90
            ),
            radialaxis=dict(visible=False)
        ),
        showlegend=False,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Astro Trading Dashboard",
        page_icon="🌐",
        layout="wide"
    )
    
    st.title("🌐 Market-Wise Planetary Transit Signals")
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0E1117;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'signals' not in st.session_state:
        st.session_state.signals = []
    
    # Symbol input by market type
    with st.expander("📊 Market Symbols Configuration", expanded=True):
        cols = st.columns(len(MARKET_CATEGORIES))
        market_symbols = {}
        
        for i, (market, default_symbols) in enumerate(MARKET_CATEGORIES.items()):
            with cols[i]:
                market_symbols[market] = st.text_area(
                    f"{market} Symbols",
                    value="\n".join(default_symbols),
                    height=150
                ).split('\n')
    
    # Flatten all symbols
    all_symbols = []
    for symbols in market_symbols.values():
        all_symbols.extend([s.strip() for s in symbols if s.strip()])
    
    # Auto-refresh control
    refresh_col1, refresh_col2 = st.columns([1, 3])
    with refresh_col1:
        refresh_rate = st.slider("Refresh (seconds)", 5, 60, 15)
    with refresh_col2:
        auto_refresh = st.checkbox("Enable live updates", True)
    
    # Dashboard placeholder
    dashboard_placeholder = st.empty()
    
    # Main loop
    while auto_refresh and all_symbols:
        start_time = time.time()
        
        # Generate alerts
        alerts = analyze_transits(all_symbols)
        st.session_state.signals = alerts
        
        # Update dashboard
        with dashboard_placeholder.container():
            display_market_dashboard(alerts)
        
        # Control refresh rate
        elapsed = time.time() - start_time
        sleep_time = max(0, refresh_rate - elapsed)
        time.sleep(sleep_time)
        
        # Manual refresh check
        if not auto_refresh:
            break
    
    # Show final state if auto-refresh is off
    if not auto_refresh and all_symbols:
        alerts = analyze_transits(all_symbols)
        st.session_state.signals = alerts
        display_market_dashboard(alerts)

if __name__ == "__main__":
    main()
