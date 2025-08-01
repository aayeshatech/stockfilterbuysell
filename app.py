import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time
import os
import numpy as np

# Dependency Management
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available - using simplified display")

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

# Market Categories with Sample Symbols
MARKET_CATEGORIES = {
    "Equity": ["NSE:RELIANCE", "NSE:TATASTEEL", "NSE:HDFCBANK", "NSE:INFY", "NSE:TCS"],
    "Commodity": ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL", "MCX:COPPER", "MCX:NATURALGAS"],
    "Index": ["NSE:NIFTY", "NSE:BANKNIFTY", "NSE:FINNIFTY", "BSE:SENSEX", "NSE:NIFTYMIDCAP"],
    "Forex": ["FX:USDINR", "FX:EURINR", "FX:GBPINR", "FX:JPYINR", "FX:AUDINR"]
}

# Planetary Rulerships
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

# Zodiac Signs
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", 
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_planet_position(planet, date_utc):
    """Get planet's position with degrees, minutes, seconds"""
    if not SWISSEPH_AVAILABLE:
        # Demo mode - simulated positions
        deg = (date_utc.hour * 15 + date_utc.minute * 0.25) % 360
        return deg, int(deg), int((deg % 1) * 60), int(((deg % 1) * 60 % 1) * 60)
    
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
    return deg, int(deg), int((deg % 1) * 60), int(((deg % 1) * 60 % 1) * 60)

def get_planet_for_symbol(symbol):
    """Determine planetary ruler for symbol"""
    symbol_key = symbol.split(':')[-1] if ':' in symbol else symbol
    for planet, keywords in PLANETARY_RULES.items():
        for keyword in keywords:
            if keyword in symbol_key.upper():
                return planet
    return None

def get_market_type(symbol):
    """Categorize symbol by market type"""
    if any(m in symbol.upper() for m in ['NSE:', 'BSE:']):
        return "Equity"
    elif 'MCX:' in symbol.upper():
        return "Commodity"
    elif any(m in symbol.upper() for m in ['NIFTY', 'SENSEX', 'INDEX']):
        return "Index"
    elif any(m in symbol.upper() for m in ['USD', 'EUR', 'GBP', 'JPY', 'INR']):
        return "Forex"
    return "Other"

def analyze_transits(symbols):
    """Generate trading signals based on transits"""
    now_utc = datetime.now(pytz.utc)
    alerts = []
    
    for symbol in symbols:
        planet = get_planet_for_symbol(symbol)
        if not planet:
            continue
            
        try:
            deg, d, m, s = get_planet_position(planet, now_utc)
            natal_pos = deg  # In production, use actual natal positions
            
            # Aspect analysis (simplified - just conjunctions)
            if abs((deg - natal_pos) % 360) <= 3:
                if planet in ['JUPITER', 'VENUS', 'MOON']:
                    signal = 'BUY'
                    reason = f"Benefic {planet} at {d}°{m}'{s}\""
                elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
                    signal = 'SELL'
                    reason = f"Challenging {planet} at {d}°{m}'{s}\""
                else:
                    signal = 'HOLD'
                    reason = f"Solar influence at {d}°{m}'{s}\""
                
                # Determine zodiac sign
                sign_idx = int(deg / 30)
                sign = ZODIAC_SIGNS[sign_idx]
                sign_pos = deg % 30
                
                alerts.append({
                    'Symbol': symbol,
                    'Market': get_market_type(symbol),
                    'Signal': signal,
                    'Planet': planet,
                    'Degree': f"{d}°{m}'{s}\"",
                    'Zodiac': f"{sign} {sign_pos:.1f}°",
                    'Time': now_utc,
                    'Reason': reason,
                    'Position': deg,
                    'Color': '#006400' if signal == 'BUY' else '#8B0000' if signal == 'SELL' else '#FFD700'
                })
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return alerts

def create_zodiac_wheel(alerts):
    """Create interactive zodiac wheel visualization"""
    if not PLOTLY_AVAILABLE or not alerts:
        return None
    
    fig = go.Figure()

    # Add zodiac signs
    for i, sign in enumerate(ZODIAC_SIGNS):
        fig.add_trace(go.Scatterpolar(
            r=[1],
            theta=[i * 30 + 15],  # Center of each sign
            mode='text',
            text=[sign],
            textfont=dict(size=14),
            hoverinfo='none',
            showlegend=False
        ))

    # Add planet markers
    for alert in alerts:
        fig.add_trace(go.Scatterpolar(
            r=[0.85],
            theta=[alert['Position']],
            mode='markers+text',
            marker=dict(
                size=20,
                color=alert['Color'],
                symbol='hexagram' if alert['Planet'] in ['RAHU', 'KETU'] else 'circle',
                line=dict(width=2, color='white')
            ),
            text=[alert['Planet']],
            textposition='middle center',
            name=f"{alert['Symbol']} - {alert['Signal']}",
            hoverinfo='text',
            hovertext=f"""
            <b>{alert['Symbol']}</b><br>
            {alert['Planet']} in {alert['Zodiac']}<br>
            Signal: <span style='color:{alert['Color']}'>{alert['Signal']}</span><br>
            {alert['Reason']}<br>
            {alert['Time'].strftime('%Y-%m-%d %H:%M:%S UTC')}
            """
        ))

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                rotation=90,
                direction='clockwise',
                tickvals=list(range(0, 360, 30)),
                ticktext=ZODIAC_SIGNS,
                showticklabels=False
            ),
            radialaxis=dict(visible=False, range=[0, 1])
        ),
        showlegend=False,
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def display_market_signals(alerts):
    """Display signals organized by market category"""
    if not alerts:
        st.info("No active signals currently")
        return
    
    # Create tabs for each market type
    tabs = st.tabs(["All Markets"] + list(MARKET_CATEGORIES.keys()))
    
    with tabs[0]:  # All Markets
        st.subheader("🌐 All Market Signals")
        display_signals_table(alerts)
        if PLOTLY_AVAILABLE:
            st.plotly_chart(create_zodiac_wheel(alerts), use_container_width=True)
    
    # Market-specific tabs
    for i, market in enumerate(MARKET_CATEGORIES.keys(), 1):
        with tabs[i]:
            st.subheader(f"📊 {market} Signals")
            market_alerts = [a for a in alerts if a['Market'] == market]
            
            if market_alerts:
                display_signals_table(market_alerts)
                if PLOTLY_AVAILABLE:
                    st.plotly_chart(create_zodiac_wheel(market_alerts), use_container_width=True)
            else:
                st.info(f"No active signals in {market}")

def display_signals_table(alerts):
    """Display signals in an interactive table"""
    if not alerts:
        return
    
    df = pd.DataFrame(alerts)
    df['Time'] = df['Time'].dt.strftime('%H:%M:%S')
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["Time", "Symbol", "Market", "Signal", "Planet", "Zodiac", "Degree", "Reason"],
                fill_color='navy',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df[col] for col in ['Time', 'Symbol', 'Market', 'Signal', 'Planet', 'Zodiac', 'Degree', 'Reason']],
                fill_color=['white', 'white', 'white', 
                          df['Color'], 'white', 'white', 'white', 'white'],
                font=dict(color=['black']*8),
                align='left'
            )
        )])
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback simple display
        for alert in alerts:
            st.markdown(
                f"""
                <div style='
                    border-left: 5px solid {alert['Color']};
                    padding: 10px;
                    margin: 5px 0;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                '>
                    <strong>{alert['Time']}</strong> | 
                    <strong>{alert['Symbol']}</strong> | 
                    <span style='color:{alert['Color']};font-weight:bold'>{alert['Signal']}</span> | 
                    {alert['Planet']} in {alert['Zodiac']} ({alert['Degree']})<br>
                    <small>{alert['Reason']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

def main():
    st.set_page_config(
        page_title="Astro Trading Dashboard",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Planetary Transit Trading Signals")
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
        background-color: #f0f2f6;
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
    
    # Symbol configuration
    with st.expander("⚙️ Symbol Configuration", expanded=True):
        cols = st.columns(len(MARKET_CATEGORIES))
        market_symbols = {}
        
        for i, (market, default_symbols) in enumerate(MARKET_CATEGORIES.items()):
            with cols[i]:
                market_symbols[market] = st.text_area(
                    f"{market} Symbols",
                    value="\n".join(default_symbols),
                    height=150,
                    help=f"Enter one {market} symbol per line"
                ).split('\n')
    
    # Flatten all symbols
    all_symbols = []
    for symbols in market_symbols.values():
        all_symbols.extend([s.strip() for s in symbols if s.strip()])
    
    # Analysis controls
    with st.expander("🔍 Analysis Controls"):
        refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 15)
        auto_refresh = st.checkbox("Enable live updates", True)
        if st.button("Run Analysis Now"):
            st.session_state.signals = analyze_transits(all_symbols)
    
    # Main display area
    if not all_symbols:
        st.warning("Please enter symbols in the configuration section")
        return
    
    if auto_refresh:
        placeholder = st.empty()
        while auto_refresh:
            start_time = time.time()
            st.session_state.signals = analyze_transits(all_symbols)
            with placeholder.container():
                display_market_signals(st.session_state.signals)
            elapsed = time.time() - start_time
            time.sleep(max(0, refresh_rate - elapsed))
    else:
        display_market_signals(st.session_state.signals)

if __name__ == "__main__":
    main()
