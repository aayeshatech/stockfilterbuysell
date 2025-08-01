"""
Advanced Astro Trading Dashboard with Real-time Signals
"""

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import logging
import yfinance as yf
import ephem
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== SYMBOL CONFIGURATION ==================
# Enhanced symbol list including all requested instruments
WATCHLIST_SYMBOLS = [
    "NSE:NIFTY", "NSE:BANKNIFTY", "NSE:RELIANCE", "NSE:TATASTEEL",
    "NSE:HDFCBANK", "NSE:INFY", "NSE:TCS", "NSE:WIPRO",
    "GC=F", "SI=F", "BTC-USD", "^DJI",  # XAUUSD, XAGUSD, BTC, Dow Jones
    "MCX:GOLD1!", "MCX:SILVER1!", "NSE:SBIN", "NSE:ICICIBANK"
]

# Planet mapping with additional symbols
PLANET_MAPPING = {
    # Commodities
    "GOLD": "Sun", "SILVER": "Moon", "CRUDEOIL": "Mars",
    "GC=F": "Sun", "SI=F": "Moon",  # XAUUSD, XAGUSD
    
    # Indices
    "NIFTY": "Jupiter", "BANKNIFTY": "Mercury", 
    "^DJI": "Sun",  # Dow Jones
    
    # Crypto
    "BTC": "Uranus", "BTC-USD": "Uranus",
    
    # Stocks
    "RELIANCE": "Jupiter", "TATA": "Venus", "HDFC": "Mercury",
    "INFY": "Saturn", "TCS": "Mercury", "WIPRO": "Mercury",
    "SBIN": "Jupiter", "ICICI": "Neptune",
    
    # Default
    "DEFAULT": "Sun"
}

# Signal configurations
EYE_SYMBOLS = {
    "STRONG_BUY": "👁️🟢✨", 
    "BUY": "👁️🟢",
    "STRONG_SELL": "👁️🔴✨",
    "SELL": "👁️🔴", 
    "HOLD": "👁️⚪",
    "WARNING": "👁️🟡"
}

PLANET_EMOJIS = {
    "Sun": "☀️", "Moon": "🌙", "Mercury": "☿", 
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃",
    "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
    "Pluto": "♇"
}

# ================== CORE FUNCTIONS ==================
@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(symbol: str) -> float:
    """Cached price fetch with enhanced error handling"""
    try:
        clean_symbol = symbol.replace("^", "").replace("1!", "").replace("=F", "")
        data = yf.Ticker(clean_symbol).history(period="1d", interval="1m", timeout=5)
        return float(data["Close"].iloc[-1]) if not data.empty else 0.0
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=512)
def get_planet_transits(planet: str, timestamp: float) -> Dict:
    """Get current and upcoming planetary transits with effects"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        
        # Current position
        planet_obj.compute(observer)
        current_strength = float(planet_obj.alt / (ephem.pi/2))
        
        # Next transit
        next_transit = observer.next_transit(planet_obj)
        next_transit_time = ephem.localtime(next_transit)
        
        # Previous transit
        prev_transit = observer.previous_transit(planet_obj)
        prev_transit_time = ephem.localtime(prev_transit)
        
        # Calculate if currently in transit window (1 hour before/after)
        in_transit_window = abs((now - next_transit_time).total_seconds()) < 3600 or \
                           abs((now - prev_transit_time).total_seconds()) < 3600
        
        return {
            "current_strength": current_strength,
            "next_transit": next_transit_time,
            "prev_transit": prev_transit_time,
            "in_transit": in_transit_window,
            "effect": get_planet_effect(planet, current_strength, in_transit_window)
        }
    except Exception as e:
        logger.warning(f"Planet calc error for {planet}: {str(e)}")
        return {
            "current_strength": 0.5,
            "next_transit": now,
            "prev_transit": now,
            "in_transit": False,
            "effect": "Neutral influence"
        }

def get_planet_effect(planet: str, strength: float, in_transit: bool) -> str:
    """Get the trading effect description for planetary position"""
    effects = {
        "Sun": {
            "high": "Strong bullish energy (Buy opportunities)",
            "low": "Lack of direction (Caution advised)",
            "transit": "High volatility expected (Trade carefully)"
        },
        "Moon": {
            "high": "Emotional buying (Short-term gains)",
            "low": "Indecisive market (Avoid new positions)",
            "transit": "Quick price swings (Scalping opportunities)"
        },
        "Mercury": {
            "high": "Good for trading (Clear signals)",
            "low": "Communication breakdown (Avoid trading)",
            "transit": "Potential reversals (Watch for pivots)"
        },
        "Jupiter": {
            "high": "Expansion phase (Strong buys)",
            "low": "Lack of growth (Avoid longs)",
            "transit": "Major moves likely (Position trading)"
        },
        "Venus": {
            "high": "Harmonious trading (Smooth trends)",
            "low": "Choppy markets (Reduce position size)",
            "transit": "Potential breakouts (Watch supports)"
        }
    }
    
    base_effect = effects.get(planet, {
        "high": "Positive influence (Look for buys)",
        "low": "Negative influence (Consider sells)",
        "transit": "Increased activity (Trade with caution)"
    })
    
    if strength > 0.7:
        return base_effect["high"]
    elif strength < 0.3:
        return base_effect["low"]
    return base_effect["transit"] if in_transit else "Neutral influence (Hold positions)"

def get_planet(symbol: str) -> str:
    """Smart planet mapping with symbol detection"""
    symbol_upper = symbol.upper()
    for key, planet in PLANET_MAPPING.items():
        if key in symbol_upper:
            return planet
    return PLANET_MAPPING["DEFAULT"]

def calculate_signal(strength: float, planet: str, in_transit: bool) -> Tuple[str, str]:
    """Enhanced signal logic with transit awareness"""
    if in_transit:
        if strength > 0.75:
            return "STRONG_BUY", f"Strong {planet} transit - Excellent buying opportunity"
        elif strength < 0.25:
            return "STRONG_SELL", f"Critical {planet} transit - Strong sell signal"
        return "WARNING", f"{planet} transit - High volatility expected"
    
    if strength > 0.8:
        return "STRONG_BUY", f"Very favorable {planet} alignment - Strong buy"
    elif strength > 0.6:
        return "BUY", f"Positive {planet} influence - Buy opportunity"
    elif strength < 0.2:
        return "STRONG_SELL", f"Critical {planet} opposition - Strong sell"
    elif strength < 0.4:
        return "SELL", f"Negative {planet} aspects - Consider selling"
    return "HOLD", f"Neutral {planet} influence - Hold positions"

def fetch_symbol_data(symbol: str, now: datetime) -> Dict:
    """Get all data for a single symbol"""
    timestamp = now.timestamp()
    planet = get_planet(symbol)
    transits = get_planet_transits(planet, timestamp)
    price = get_live_price(symbol)
    
    signal, reason = calculate_signal(
        transits["current_strength"], 
        planet,
        transits["in_transit"]
    )
    
    return {
        "symbol": symbol,
        "planet": planet,
        "price": price,
        "signal": signal,
        "reason": reason,
        "strength": transits["current_strength"],
        "next_transit": transits["next_transit"],
        "in_transit": transits["in_transit"],
        "effect": transits["effect"],
        "planet_emoji": PLANET_EMOJIS.get(planet, "🪐")
    }

def fetch_all_data(symbols: List[str], now: datetime) -> List[Dict]:
    """Parallel data fetching"""
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda s: fetch_symbol_data(s, now), symbols))
        return sorted(results, key=lambda x: x["strength"], reverse=True)

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Astro Trading Pro",
        layout="wide",
        page_icon="🔮",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .symbol-card {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-left: 5px solid;
        }
        .strong-buy { border-color: #00aa00; background-color: #f0fff0; }
        .buy { border-color: #00cc00; background-color: #e6ffe6; }
        .strong-sell { border-color: #aa0000; background-color: #ffe6e6; }
        .sell { border-color: #cc0000; background-color: #fff0f0; }
        .warning { border-color: #ffaa00; background-color: #fff9e6; }
        .hold { border-color: #888888; background-color: #f5f5f5; }
        .transit-active { 
            animation: pulse 2s infinite;
            border: 2px solid #0066cc;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0,150,255,0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0,150,255,0); }
            100% { box-shadow: 0 0 0 0 rgba(0,150,255,0); }
        }
        .price-up { color: #00aa00; font-weight: bold; }
        .price-down { color: #cc0000; font-weight: bold; }
        .price-neutral { color: #888888; }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.title("🪐 Astro Controls")
        
        # Symbol selection
        selected_symbols = st.multiselect(
            "Select Symbols",
            WATCHLIST_SYMBOLS,
            default=WATCHLIST_SYMBOLS
        )
        
        # Display filters
        st.markdown("---")
        st.markdown("**Signal Filters**")
        min_confidence = st.slider(
            "Minimum Confidence", 
            0, 100, 50
        )
        
        signal_filter = st.multiselect(
            "Show Signals",
            ["STRONG_BUY", "BUY", "WARNING", "HOLD", "SELL", "STRONG_SELL"],
            default=["STRONG_BUY", "BUY", "STRONG_SELL", "SELL"]
        )
        
        # Live mode controls
        st.markdown("---")
        st.markdown("**Live Mode Settings**")
        live_mode = st.checkbox("Enable Live Updates", True)
        refresh_rate = st.selectbox(
            "Update Frequency",
            [15, 30, 60, 120],
            index=1
        )
        
        # Current time display
        st.markdown("---")
        current_time = datetime.now(pytz.utc)
        st.markdown(f"**System Time:** {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Main content area
    st.title("🌌 Live Astro Trading Dashboard")
    
    # Create placeholder for dynamic content
    content_placeholder = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            
            # Fetch data
            with st.spinner("Calculating planetary alignments..."):
                all_data = fetch_all_data(selected_symbols, now)
            
            # Filter data
            filtered_data = [
                d for d in all_data 
                if (d["strength"] >= min_confidence/100) and 
                (d["signal"] in signal_filter)
            ]
            
            # Display in placeholder
            with content_placeholder.container():
                # Current Transits Section
                current_transits = [d for d in all_data if d["in_transit"]]
                if current_transits:
                    st.markdown("### 🌠 Active Planetary Transits")
                    cols = st.columns(min(4, len(current_transits)))
                    for i, transit in enumerate(current_transits):
                        with cols[i % len(cols)]:
                            transit_class = "transit-active " + transit["signal"].lower().replace("_", "-")
                            st.markdown(f"""
                            <div class="symbol-card {transit_class}">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="font-size:1.5rem">{transit['planet_emoji']}</span>
                                    <h3>{transit['planet']}</h3>
                                </div>
                                <p><strong>{transit['symbol']}</strong></p>
                                <p>{transit['effect']}</p>
                                <p>Until: {transit['next_transit'].strftime('%H:%M UTC')}</p>
                                <p><strong>{EYE_SYMBOLS[transit['signal']]} {transit['signal'].replace('_', ' ')}</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Upcoming Transits
                upcoming_transits = []
                for data in all_data:
                    if (data["next_transit"] - now).total_seconds() < 8*3600 and not data["in_transit"]:
                        upcoming_transits.append(data)
                
                if upcoming_transits:
                    st.markdown("### 🚀 Upcoming Transits (Next 8 Hours)")
                    upcoming_transits.sort(key=lambda x: x["next_transit"])
                    cols = st.columns(min(4, len(upcoming_transits)))
                    for i, transit in enumerate(upcoming_transits):
                        with cols[i % len(cols)]:
                            time_diff = (transit["next_transit"] - now).total_seconds()/3600
                            st.markdown(f"""
                            <div class="symbol-card">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="font-size:1.2rem">{transit['planet_emoji']}</span>
                                    <h4>{transit['planet']}</h4>
                                </div>
                                <p><strong>{transit['symbol']}</strong></p>
                                <p>In {time_diff:.1f} hours</p>
                                <p>{transit['effect']}</p>
                                <p>Potential: {transit['signal'].replace('_', ' ')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Trading Signals
                st.markdown("### 📈 Trading Signals")
                
                if not filtered_data:
                    st.warning("No signals match current filters")
                else:
                    # Group by signal type
                    signal_groups = {sig: [] for sig in EYE_SYMBOLS.keys()}
                    for data in filtered_data:
                        signal_groups[data["signal"]].append(data)
                    
                    for signal_type, signals in signal_groups.items():
                        if signals:
                            st.markdown(f"#### {EYE_SYMBOLS[signal_type]} {signal_type.replace('_', ' ')} ({len(signals)})")
                            
                            num_cols = min(4, max(2, 6 - len(signals)//3))
                            cols = st.columns(num_cols)
                            
                            for i, data in enumerate(signals):
                                with cols[i % num_cols]:
                                    card_class = signal_type.lower().replace("_", "-")
                                    price_display = f"{data['price']:,.2f}" if data['price'] > 0 else "N/A"
                                    st.markdown(f"""
                                    <div class="symbol-card {card_class}">
                                        <div style="display:flex; align-items:center; gap:10px;">
                                            <span style="font-size:1.2rem">{data['planet_emoji']}</span>
                                            <h4>{data['symbol']}</h4>
                                        </div>
                                        <p>Price: <span class="price-{'up' if data['strength'] > 0.7 else 'down' if data['strength'] < 0.3 else 'neutral'}">{price_display}</span></p>
                                        <p><strong>{EYE_SYMBOLS[data['signal']]} {data['signal'].replace('_', ' ')}</strong></p>
                                        <p>Confidence: {data['strength']:.0%}</p>
                                        <small>{data['reason']}</small>
                                        <div style="margin-top:10px; padding:8px; background:#f8f9fa; border-radius:5px;">
                                            <small>Next Transit: {data['next_transit'].strftime('%H:%M UTC')}</small>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                
                # Footer with performance info
                st.markdown("---")
                st.caption(f"""
                Last update: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | 
                Processed {len(selected_symbols)} symbols in {time.time()-start_time:.2f}s | 
                Showing {len(filtered_data)} signals
                """)
            
            if not live_mode:
                break
            time.sleep(refresh_rate)
    
    except Exception as e:
        logger.error(f"App error: {str(e)}")
        st.error("System error - please try again later")
        st.exception(e)

if __name__ == "__main__":
    main()
