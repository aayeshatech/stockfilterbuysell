import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import time
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Check if swisseph is available
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    st.warning("Swiss Ephemeris not available - running in demo mode")

# Configuration
EPHE_PATH = './ephe'

# Planetary associations
PLANETARY_RULES = {
    'SUN': ['NIFTY', 'BANKNIFTY', 'GOLD', 'SILVER', 'INDEX'],
    'MOON': ['FINANCE', 'FMCG', 'BANK', 'CURRENCY'],
    'MERCURY': ['IT', 'TECH', 'PHARMA', 'MEDIA', 'COMM'],
    'VENUS': ['CONSUMER', 'AUTO', 'REALTY', 'LUXURY'],
    'MARS': ['METAL', 'ENERGY', 'OIL', 'DEFENSE'],
    'JUPITER': ['BANK', 'FINANCE', 'FMCG', 'EDUCATION'],
    'SATURN': ['INFRA', 'COMMODITIES', 'STEEL', 'CEMENT'],
    'RAHU': ['CRYPTO', 'VIX', 'SPECULATIVE', 'NEWAGE'],
    'KETU': ['PHARMA', 'METAL', 'PSU', 'SPECIALITY']
}

# Initialize Swiss Ephemeris
if SWISSEPH_AVAILABLE:
    try:
        swe.set_ephe_path(EPHE_PATH)
    except Exception as e:
        st.error(f"Error initializing Swiss Ephemeris: {e}")

def get_planet_position(planet, date_utc):
    """Get planet's longitude position"""
    if not SWISSEPH_AVAILABLE:
        return (date_utc.hour * 15 + date_utc.minute * 0.25) % 360
    
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 
                   date_utc.hour + date_utc.minute/60 + date_utc.second/3600)
    try:
        planet_code = getattr(swe, planet)
    except AttributeError:
        if planet == 'RAHU':
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
            return pos[0]
        elif planet == 'KETU':
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
            return (pos[0] + 180) % 360
        else:
            raise ValueError(f"Unknown planet: {planet}")
    
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    pos, _ = swe.calc_ut(jd, planet_code, flags)
    return pos[0]

def get_planet_for_symbol(symbol):
    """Determine planetary ruler for symbol"""
    symbol_upper = symbol.upper()
    for planet, keywords in PLANETARY_RULES.items():
        for keyword in keywords:
            if keyword in symbol_upper:
                return planet
    return None

def analyze_transits(symbols):
    """Generate trading signals based on transits"""
    now_utc = datetime.now(pytz.utc)
    alerts = []
    
    for symbol in symbols:
        planet = get_planet_for_symbol(symbol)
        if not planet:
            continue
            
        try:
            current_pos = get_planet_position(planet, now_utc)
            natal_pos = current_pos  # Replace with actual natal positions
            
            if abs((current_pos - natal_pos) % 360) <= 3:
                if planet in ['JUPITER', 'VENUS', 'MOON']:
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'BUY',
                        'Planet': planet,
                        'Time': now_utc,
                        'Position': current_pos
                    })
                elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'SELL',
                        'Planet': planet,
                        'Time': now_utc,
                        'Position': current_pos
                    })
                elif planet == 'SUN':
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'HOLD',
                        'Planet': planet,
                        'Time': now_utc,
                        'Position': current_pos
                    })
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return alerts

def create_astro_chart(alerts):
    """Create real-time astrological visualization"""
    if not alerts:
        return None
    
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'polar'}, {'type': 'xy'}]])
    
    # Polar chart for planetary positions
    planets = [alert['Planet'] for alert in alerts]
    positions = [alert['Position'] for alert in alerts]
    signals = [alert['Signal'] for alert in alerts]
    colors = ['darkgreen' if s == 'BUY' else 'crimson' if s == 'SELL' else 'gold' for s in signals]
    
    fig.add_trace(go.Scatterpolar(
        r=[1]*len(planets),
        theta=positions,
        text=planets,
        marker=dict(size=20, color=colors),
        name='Planets',
        subplot='polar'
    ), 1, 1)
    
    fig.update_polars(
        radialaxis=dict(visible=False),
        angularaxis=dict(
            direction='clockwise',
            rotation=90
        )
    )
    
    # Ticker-style display
    ticker_df = pd.DataFrame(alerts)
    ticker_df['Time'] = ticker_df['Time'].dt.strftime('%H:%M:%S')
    
    fig.add_trace(go.Table(
        header=dict(
            values=['Time', 'Symbol', 'Signal', 'Planet'],
            fill_color='navy',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[ticker_df['Time'], ticker_df['Symbol'], 
                   ticker_df['Signal'], ticker_df['Planet']],
            fill_color=[['white', 'lightgray']*len(ticker_df),
                        ['white', 'lightgray']*len(ticker_df),
                        [['darkgreen' if x == 'BUY' else 'crimson' if x == 'SELL' else 'gold' 
                          for x in ticker_df['Signal']]],
                        ['white', 'lightgray']*len(ticker_df)],
            font=dict(color=['black', 'black', 'white', 'black'])
        ),
        columnwidth=[1, 2, 1, 1]
    ), 1, 2)
    
    fig.update_layout(
        title='Live Astro Trading Signals',
        height=500,
        showlegend=False,
        polar=dict(
            domain=dict(x=[0, 0.45])
        )
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Live Astro Trader",
        page_icon="🌌",
        layout="wide"
    )
    
    st.title("🌠 Live Astrological Trading Signals")
    st.markdown("""
    <style>
    .stAlert { padding: 10px; border-radius: 5px; }
    .buy-signal { background-color: #006400; color: white; padding: 5px; border-radius: 3px; }
    .sell-signal { background-color: #8B0000; color: white; padding: 5px; border-radius: 3px; }
    .hold-signal { background-color: #FFD700; color: black; padding: 5px; border-radius: 3px; }
    .ticker { 
        background-color: #0E1117;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        overflow-x: auto;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Real-time display placeholder
    chart_placeholder = st.empty()
    ticker_placeholder = st.empty()
    alert_history = st.empty()
    
    # Symbol input
    with st.expander("🔮 Symbol Configuration", expanded=True):
        default_symbols = """NSE:NIFTY,NSE:BANKNIFTY,NSE:RELIANCE,NSE:TATASTEEL,NSE:HDFCBANK,
                         MCX:GOLD1!,MCX:SILVER1!,NSE:INFY,NSE:TCS,NSE:HINDUNILVR"""
        symbol_input = st.text_area("Enter symbols (comma separated)", value=default_symbols)
        symbols = [s.strip() for s in symbol_input.split(',') if s.strip()]
        
    # Auto-refresh control
    refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 15)
    auto_refresh = st.checkbox("Enable auto-refresh", True)
    
    # Initialize history
    if 'history' not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=['Time', 'Symbol', 'Signal', 'Planet'])
    
    # Main loop
    while auto_refresh:
        start_time = time.time()
        
        # Generate alerts
        alerts = analyze_transits(symbols)
        now = datetime.now(pytz.utc).strftime('%H:%M:%S')
        
        if alerts:
            # Update history
            new_alerts = pd.DataFrame(alerts)
            new_alerts['Time'] = new_alerts['Time'].dt.strftime('%H:%M:%S')
            st.session_state.history = pd.concat(
                [st.session_state.history, new_alerts[['Time', 'Symbol', 'Signal', 'Planet']]]
            ).drop_duplicates().tail(50)  # Keep last 50 alerts
            
            # Visualizations
            fig = create_astro_chart(alerts)
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Ticker display
            ticker_html = "<div class='ticker'>"
            for alert in alerts[-10:]:  # Show last 10 alerts in ticker
                signal_class = alert['Signal'].lower() + "-signal"
                ticker_html += f"""
                <span style='margin-right: 20px;'>
                    [{alert['Time'].strftime('%H:%M:%S')}] 
                    <strong>{alert['Symbol']}</strong> 
                    <span class='{signal_class}'>{alert['Signal']}</span> 
                    ({alert['Planet']})
                </span>"""
            ticker_html += "</div>"
            ticker_placeholder.markdown(ticker_html, unsafe_allow_html=True)
            
            # Alert history
            alert_history.dataframe(
                st.session_state.history.style.applymap(
                    lambda x: 'background-color: darkgreen; color: white' if x == 'BUY' else
                             'background-color: crimson; color: white' if x == 'SELL' else
                             'background-color: gold; color: black',
                    subset=['Signal']
                ),
                height=500,
                use_container_width=True
            )
        else:
            chart_placeholder.info("No significant transits detected")
            ticker_placeholder.info("Waiting for signals...")
        
        # Control refresh rate
        elapsed = time.time() - start_time
        sleep_time = max(0, refresh_rate - elapsed)
        time.sleep(sleep_time)
        
        # Manual refresh check
        if not auto_refresh:
            break

if __name__ == "__main__":
    main()
