import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

# Try importing optional packages with error handling
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    st.error("yfinance package not found. Install with: pip install yfinance")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("plotly package not found. Install with: pip install plotly")

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    st.error("pyswisseph package not found. Install with: pip install pyswisseph")

# Initialize Swiss Ephemeris
def init_swisseph():
    """Initialize Swiss Ephemeris with proper error handling"""
    if not SWISSEPH_AVAILABLE:
        return False
        
    try:
        # Create ephemeris directory if it doesn't exist
        ephe_dir = os.path.join(os.path.dirname(__file__), 'ephe')
        if not os.path.exists(ephe_dir):
            os.makedirs(ephe_dir)
        
        # Set ephemeris path
        swe.set_ephe_path(ephe_dir.encode('utf-8'))
        # Test initialization
        swe.julday(2023, 1, 1)
        return True
    except Exception as e:
        st.error(f"Swiss Ephemeris initialization failed: {str(e)}")
        return False

# Initialize if not already done
if 'swisseph_initialized' not in st.session_state:
    st.session_state.swisseph_initialized = init_swisseph()

# Page configuration
st.set_page_config(
    page_title="Astro Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .signal-bullish {
        color: #2ca02c;
        font-weight: bold;
    }
    .signal-bearish {
        color: #d62728;
        font-weight: bold;
    }
    .signal-neutral {
        color: #7f7f7f;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .timeline-dot {
        height: 15px;
        width: 15px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Load watchlist
def load_watchlist():
    """Load your EYE FUTURE WATCHLIST"""
    watchlist = {
        'Nifty': '^NSEI',
        'BankNifty': '^NSEBANK',
        'Gold': 'GC=F',
        'Crude': 'CL=F',
        'Reliance': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'HDFC Bank': 'HDFCBANK.NS',
        'Infosys': 'INFY.NS',
        'ICICI Bank': 'ICICIBANK.NS',
        'Kotak Bank': 'KOTAKBANK.NS',
        'Axis Bank': 'AXISBANK.NS',
        'SBI': 'SBIN.NS',
        'Wipro': 'WIPRO.NS',
        'HCL Tech': 'HCLTECH.NS',
        'Tech Mahindra': 'TECHM.NS',
        'L&T': 'LT.NS',
        'Bajaj Finance': 'BAJFINANCE.NS',
        'HDFC': 'HDFC.NS',
        'ITC': 'ITC.NS'
    }
    
    sectors = {
        'Nifty': 'Index',
        'BankNifty': 'Banking',
        'Gold': 'Commodity',
        'Crude': 'Commodity',
        'Reliance': 'Energy',
        'TCS': 'IT',
        'HDFC Bank': 'Banking',
        'Infosys': 'IT',
        'ICICI Bank': 'Banking',
        'Kotak Bank': 'Banking',
        'Axis Bank': 'Banking',
        'SBI': 'Banking',
        'Wipro': 'IT',
        'HCL Tech': 'IT',
        'Tech Mahindra': 'IT',
        'L&T': 'Infrastructure',
        'Bajaj Finance': 'Financial',
        'HDFC': 'Financial',
        'ITC': 'FMCG'
    }
    
    return watchlist, sectors

# Calculate planetary positions
def calculate_planetary_positions(date_time):
    """Calculate planetary positions for given datetime"""
    if not st.session_state.swisseph_initialized or not SWISSEPH_AVAILABLE:
        return {}
    
    try:
        # Convert to Julian day
        jd = swe.julday(
            date_time.year, date_time.month, date_time.day,
            date_time.hour + date_time.minute/60.0
        )
        
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE,
            'Ketu': -swe.MEAN_NODE
        }
        
        positions = {}
        for name, planet_id in planets.items():
            pos, _ = swe.calc_ut(jd, planet_id)
            positions[name] = pos[0]  # Longitude
        
        return positions
    except Exception as e:
        st.error(f"Error calculating planetary positions: {str(e)}")
        return {}

# Calculate planetary aspects
def calculate_planetary_aspects(positions):
    """Calculate significant planetary aspects"""
    aspects = []
    
    # Define aspect types and their orbs
    aspect_types = {
        'Conjunction': (0, 8),
        'Opposition': (180, 8),
        'Trine': (120, 6),
        'Square': (90, 6),
        'Sextile': (60, 4)
    }
    
    planet_combinations = [
        ('Sun', 'Moon'), ('Sun', 'Mercury'), ('Sun', 'Venus'), ('Sun', 'Mars'),
        ('Sun', 'Jupiter'), ('Sun', 'Saturn'), ('Moon', 'Mercury'), ('Moon', 'Venus'),
        ('Moon', 'Mars'), ('Moon', 'Jupiter'), ('Moon', 'Saturn'), ('Mercury', 'Venus'),
        ('Mercury', 'Mars'), ('Mercury', 'Jupiter'), ('Mercury', 'Saturn'),
        ('Venus', 'Mars'), ('Venus', 'Jupiter'), ('Venus', 'Saturn'),
        ('Mars', 'Jupiter'), ('Mars', 'Saturn'), ('Jupiter', 'Saturn'),
        ('Sun', 'Rahu'), ('Moon', 'Rahu'), ('Mars', 'Rahu'), ('Saturn', 'Rahu'),
        ('Sun', 'Ketu'), ('Moon', 'Ketu'), ('Mars', 'Ketu'), ('Saturn', 'Ketu')
    ]
    
    for planet1, planet2 in planet_combinations:
        if planet1 in positions and planet2 in positions:
            pos1 = positions[planet1]
            pos2 = positions[planet2]
            
            # Calculate angular separation
            angle = abs(pos1 - pos2)
            if angle > 180:
                angle = 360 - angle
            
            # Check for aspects
            for aspect_name, (target_angle, orb) in aspect_types.items():
                if abs(angle - target_angle) <= orb:
                    # Calculate aspect strength (1.0 at exact aspect, 0.0 at orb limit)
                    strength = 1.0 - (abs(angle - target_angle) / orb)
                    
                    aspects.append({
                        'planet1': planet1,
                        'planet2': planet2,
                        'aspect': aspect_name,
                        'angle': angle,
                        'strength': strength,
                        'orb_used': abs(angle - target_angle)
                    })
    
    return aspects

# Generate trading signals
def generate_trading_signals(aspects, symbol, sector, current_time):
    """Generate bullish/bearish signals based on planetary aspects"""
    signals = []
    
    # Define aspect interpretations
    bullish_aspects = [
        ('Jupiter', 'Venus', 'any'),
        ('Jupiter', 'Sun', 'any'),
        ('Venus', 'Sun', 'any'),
        ('Jupiter', 'Moon', 'Trine'),
        ('Venus', 'Moon', 'Trine'),
        ('Sun', 'Moon', 'Trine')
    ]
    
    bearish_aspects = [
        ('Saturn', 'Mars', 'any'),
        ('Saturn', 'Sun', 'any'),
        ('Mars', 'Saturn', 'any'),
        ('Saturn', 'Moon', 'Square'),
        ('Mars', 'Moon', 'Square'),
        ('Rahu', 'Sun', 'any'),
        ('Rahu', 'Moon', 'any'),
        ('Ketu', 'Sun', 'any'),
        ('Ketu', 'Moon', 'any')
    ]
    
    # Sector-specific rules
    sector_rules = {
        'Banking': {
            'bullish': [('Jupiter', 'any', 'Trine'), ('Venus', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Mars', 'any', 'Square')]
        },
        'IT': {
            'bullish': [('Mercury', 'any', 'Trine'), ('Jupiter', 'Mercury', 'any')],
            'bearish': [('Saturn', 'Mercury', 'any'), ('Rahu', 'Mercury', 'any')]
        },
        'Energy': {
            'bullish': [('Mars', 'any', 'Trine'), ('Sun', 'Mars', 'any')],
            'bearish': [('Saturn', 'Mars', 'any'), ('Rahu', 'Mars', 'any')]
        },
        'Commodity': {
            'bullish': [('Venus', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Mars', 'any', 'Square')]
        },
        'Financial': {
            'bullish': [('Jupiter', 'any', 'Trine'), ('Venus', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        }
    }
    
    # Check general aspects
    for aspect in aspects:
        p1, p2, aspect_type = aspect['planet1'], aspect['planet2'], aspect['aspect']
        strength = aspect['strength']
        
        # Check bullish signals
        for bp1, bp2, btype in bullish_aspects:
            if ((p1 == bp1 and p2 == bp2) or (p1 == bp2 and p2 == bp1)) and \
               (btype == 'any' or aspect_type == btype):
                signals.append({
                    'type': 'bullish',
                    'strength': strength,
                    'reason': f"{p1}-{p2} {aspect_type}",
                    'time': current_time.strftime("%H:%M")
                })
        
        # Check bearish signals
        for sp1, sp2, stype in bearish_aspects:
            if ((p1 == sp1 and p2 == sp2) or (p1 == sp2 and p2 == sp1)) and \
               (stype == 'any' or aspect_type == stype):
                signals.append({
                    'type': 'bearish',
                    'strength': strength,
                    'reason': f"{p1}-{p2} {aspect_type}",
                    'time': current_time.strftime("%H:%M")
                })
    
    # Check sector-specific rules
    if sector in sector_rules:
        for aspect in aspects:
            p1, p2, aspect_type = aspect['planet1'], aspect['planet2'], aspect['aspect']
            strength = aspect['strength']
            
            # Sector bullish
            for bp1, btype, batype in sector_rules[sector]['bullish']:
                if (p1 == bp1 or p2 == bp1) and (btype == 'any' or aspect_type == batype):
                    signals.append({
                        'type': 'bullish',
                        'strength': strength * 1.2,  # Boost sector signals
                        'reason': f"{sector}: {p1}-{p2} {aspect_type}",
                        'time': current_time.strftime("%H:%M")
                    })
            
            # Sector bearish
            for sp1, stype, satype in sector_rules[sector]['bearish']:
                if (p1 == sp1 or p2 == sp1) and (stype == 'any' or aspect_type == satype):
                    signals.append({
                        'type': 'bearish',
                        'strength': strength * 1.2,  # Boost sector signals
                        'reason': f"{sector}: {p1}-{p2} {aspect_type}",
                        'time': current_time.strftime("%H:%M")
                    })
    
    return signals

# Get market data
def get_market_data(symbol, ticker):
    """Get current market data for a symbol"""
    if not YFINANCE_AVAILABLE:
        return {
            'price': None,
            'change': None,
            'change_pct': None,
            'volume': None
        }
        
    try:
        ticker_data = yf.Ticker(ticker)
        hist = ticker_data.history(period="2d")
        
        if len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            return {
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': hist['Volume'].iloc[-1] if 'Volume' in hist else None
            }
        else:
            return {
                'price': hist['Close'].iloc[-1] if len(hist) == 1 else None,
                'change': None,
                'change_pct': None,
                'volume': None
            }
    except Exception as e:
        return {
            'price': None,
            'change': None,
            'change_pct': None,
            'volume': None
        }

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🌌 Planetary Transit Trading Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:gray;">Real-time bullish/bearish signals based on planetary aspects</p>', unsafe_allow_html=True)
    
    # Load watchlist
    watchlist, sectors = load_watchlist()
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Refresh settings
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 30, 300, 60)
    
    # Sector filter
    all_sectors = list(set(sectors.values()))
    selected_sectors = st.sidebar.multiselect(
        "Filter by Sector",
        options=all_sectors,
        default=all_sectors
    )
    
    # Signal strength filter
    min_strength = st.sidebar.slider("Minimum Signal Strength", 0.1, 1.0, 0.5)
    
    # Main content area
    col1, col2, col3 = st.columns([3, 2, 2])
    
    # Current time
    current_time = datetime.now()
    
    # Calculate planetary positions and aspects
    positions = calculate_planetary_positions(current_time)
    aspects = calculate_planetary_aspects(positions)
    
    # Generate signals for watchlist
    signal_data = []
    for symbol, ticker in watchlist.items():
        sector = sectors.get(symbol, 'Unknown')
        if sector not in selected_sectors:
            continue
            
        # Get market data
        market_data = get_market_data(symbol, ticker)
        
        # Generate signals
        signals = generate_trading_signals(aspects, symbol, sector, current_time)
        
        # Filter signals by strength
        signals = [s for s in signals if s['strength'] >= min_strength]
        
        # Calculate overall signal
        bullish_strength = sum(s['strength'] for s in signals if s['type'] == 'bullish')
        bearish_strength = sum(s['strength'] for s in signals if s['type'] == 'bearish')
        
        if bullish_strength > bearish_strength:
            overall_signal = "🐂 Bullish"
            signal_class = "signal-bullish"
        elif bearish_strength > bullish_strength:
            overall_signal = "🐻 Bearish"
            signal_class = "signal-bearish"
        else:
            overall_signal = "⚖ Neutral"
            signal_class = "signal-neutral"
        
        signal_data.append({
            'Symbol': symbol,
            'Sector': sector,
            'Price': market_data['price'],
            'Change %': market_data['change_pct'],
            'Signal': overall_signal,
            'Signal Class': signal_class,
            'Bullish Strength': round(bullish_strength, 2),
            'Bearish Strength': round(bearish_strength, 2),
            'Recent Signals': ", ".join([f"{s['reason']} ({s['time']})" for s in signals[:3]]),
            'Signals': signals
        })
    
    # Display signals table
    with col1:
        st.header("Watchlist Signals")
        
        if signal_data:
            # Create DataFrame
            signal_df = pd.DataFrame(signal_data)
            
            # Format columns
            signal_df['Price'] = signal_df['Price'].apply(lambda x: f"₹{x:.2f}" if x is not None else "N/A")
            signal_df['Change %'] = signal_df['Change %'].apply(lambda x: f"{x:.2f}%" if x is not None else "N/A")
            
            # Display with styling
            st.dataframe(
                signal_df.style.applymap(
                    lambda x: f"color: {'green' if 'Bullish' in x else 'red' if 'Bearish' in x else 'gray'}",
                    subset=['Signal']
                ),
                use_container_width=True,
                height=600
            )
        else:
            st.info("No signals generated for selected filters")
    
    # Display planetary aspects
    with col2:
        st.header("Planetary Aspects")
        
        if aspects:
            aspect_df = pd.DataFrame(aspects)
            aspect_df = aspect_df.sort_values('strength', ascending=False)
            aspect_df['strength'] = aspect_df['strength'].apply(lambda x: f"{x:.2f}")
            aspect_df['angle'] = aspect_df['angle'].apply(lambda x: f"{x:.1f}°")
            
            st.dataframe(
                aspect_df[['planet1', 'planet2', 'aspect', 'angle', 'strength']],
                use_container_width=True
            )
        else:
            st.info("No significant aspects at this time")
    
    # Display sector overview
    with col3:
        st.header("Sector Overview")
        
        # Calculate sector sentiment
        sector_sentiment = {}
        for sector in selected_sectors:
            sector_signals = [s for s in signal_data if s['Sector'] == sector]
            if sector_signals:
                bullish = sum(1 for s in sector_signals if "Bullish" in s['Signal'])
                bearish = sum(1 for s in sector_signals if "Bearish" in s['Signal'])
                neutral = len(sector_signals) - bullish - bearish
                
                sector_sentiment[sector] = {
                    'Bullish': bullish,
                    'Bearish': bearish,
                    'Neutral': neutral,
                    'Total': len(sector_signals)
                }
        
        if sector_sentiment:
            sentiment_df = pd.DataFrame.from_dict(sector_sentiment, orient='index')
            st.dataframe(sentiment_df, use_container_width=True)
            
            # Create pie chart if plotly is available
            if PLOTLY_AVAILABLE:
                fig = px.pie(
                    values=[sum(d['Bullish'] for d in sector_sentiment.values()),
                           sum(d['Bearish'] for d in sector_sentiment.values()),
                           sum(d['Neutral'] for d in sector_sentiment.values())],
                    names=['Bullish', 'Bearish', 'Neutral'],
                    title="Overall Market Sentiment",
                    color_discrete_map={'Bullish': 'green', 'Bearish': 'red', 'Neutral': 'gray'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Plotly not available - cannot display charts")
    
    # Timeline section
    st.header("Intraday Signal Timeline")
    
    # Generate timeline data for the day
    timeline_data = []
    start_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)  # Market open
    end_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)    # Market close
    
    # Generate signals at 15-minute intervals
    time_point = start_time
    while time_point <= end_time and time_point <= current_time:
        # Calculate positions at this time
        positions_at_time = calculate_planetary_positions(time_point)
        aspects_at_time = calculate_planetary_aspects(positions_at_time)
        
        # Generate signals for all symbols
        for symbol, ticker in watchlist.items():
            sector = sectors.get(symbol, 'Unknown')
            if sector not in selected_sectors:
                continue
                
            signals = generate_trading_signals(aspects_at_time, symbol, sector, time_point)
            signals = [s for s in signals if s['strength'] >= min_strength]
            
            for signal in signals:
                timeline_data.append({
                    'Time': time_point.strftime("%H:%M"),
                    'Symbol': symbol,
                    'Signal': signal['type'],
                    'Strength': signal['strength'],
                    'Reason': signal['reason']
                })
        
        # Next time point
        time_point += timedelta(minutes=15)
    
    # Display timeline
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create scatter plot if plotly is available
        if PLOTLY_AVAILABLE:
            fig = px.scatter(
                timeline_df,
                x='Time',
                y='Symbol',
                color='Signal',
                size='Strength',
                color_discrete_map={'bullish': 'green', 'bearish': 'red'},
                title="Signal Timeline Throughout the Day",
                height=400
            )
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Symbol",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Plotly not available - cannot display timeline chart")
        
        # Show recent signals in a table
        st.subheader("Recent Signals")
        recent_signals = sorted(timeline_data, key=lambda x: x['Time'], reverse=True)[:10]
        recent_df = pd.DataFrame(recent_signals)
        recent_df['Strength'] = recent_df['Strength'].apply(lambda x: f"{x:.2f}")
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No signals generated in the timeline")
    
    # Auto-refresh
    if auto_refresh:
        st.session_state.last_refresh = time.time()
        time_elapsed = time.time() - st.session_state.last_refresh
        
        if time_elapsed >= refresh_interval:
            st.rerun()  # Updated from st.experimental_rerun()
        
        # Show refresh countdown
        remaining_time = refresh_interval - time_elapsed
        st.sidebar.markdown(f"**Next refresh in:** {int(remaining_time)} seconds")

if __name__ == "__main__":
    main()
