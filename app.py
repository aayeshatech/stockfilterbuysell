"""
Global Markets Astro Trading Dashboard - Focus on Commodities & Indices
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

# ================== GLOBAL MARKETS CONFIGURATION ==================
GLOBAL_SYMBOLS = [
    "GC=F",  # Gold
    "SI=F",  # Silver
    "CL=F",  # Crude Oil
    "NG=F",  # Natural Gas
    "BTC-USD",  # Bitcoin
    "^DJI",  # Dow Jones
    "^GSPC",  # S&P 500
    "^IXIC",  # Nasdaq
]

PLANET_MAPPING = {
    # Commodities
    "GC=F": "Sun", "GOLD": "Sun", "XAUUSD": "Sun",
    "SI=F": "Moon", "SILVER": "Moon", "XAGUSD": "Moon",
    "CL=F": "Mars", "CRUDE": "Mars", "OIL": "Mars",
    "NG=F": "Venus", "NATURALGAS": "Venus",
    
    # Crypto
    "BTC": "Uranus", "BTC-USD": "Uranus",
    
    # Indices
    "^DJI": "Jupiter", "DOW": "Jupiter",
    "^GSPC": "Saturn", "SPX": "Saturn",
    "^IXIC": "Mercury", "NASDAQ": "Mercury",
    
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
        clean_symbol = symbol.replace("^", "").replace("=F", "")
        data = yf.Ticker(clean_symbol).history(period="1d", interval="1m", timeout=5)
        return float(data["Close"].iloc[-1]) if not data.empty else 0.0
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=128)
def get_planet_transits(planet: str, timestamp: float) -> Dict:
    """Get current planetary positions and upcoming transits"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        
        planet_obj.compute(observer)
        current_strength = float(planet_obj.alt / (ephem.pi/2))
        
        # Calculate next 3 transits today
        transits = []
        transit_time = observer.next_transit(planet_obj)
        
        for _ in range(3):
            transits.append(ephem.localtime(transit_time))
            transit_time = observer.next_transit(planet_obj, start=transit_time + ephem.minute)
        
        # Check if currently in transit (1 hour window)
        in_transit = any(abs((now - t).total_seconds()) < 3600 for t in transits[:1])
        
        return {
            "current_strength": current_strength,
            "next_transits": transits,
            "in_transit": in_transit,
            "effect": get_planet_effect(planet, current_strength, in_transit)
        }
    except Exception as e:
        logger.warning(f"Planet calc error for {planet}: {str(e)}")
        return {
            "current_strength": 0.5,
            "next_transits": [now, now + timedelta(hours=6), now + timedelta(hours=12)],
            "in_transit": False,
            "effect": "Neutral influence"
        }

def get_planet_effect(planet: str, strength: float, in_transit: bool) -> str:
    """Get market effect description for planetary position"""
    effects = {
        "Sun": {
            "high": "Strong bullish energy (Buy commodities)",
            "low": "Lack of direction (Reduce positions)",
            "transit": "High volatility expected (Trade carefully)"
        },
        "Moon": {
            "high": "Emotional buying (Short-term trades)",
            "low": "Indecisive markets (Avoid new entries)",
            "transit": "Quick reversals likely (Watch pivots)"
        },
        "Mars": {
            "high": "Strong momentum (Trend following)",
            "low": "Energy depletion (Avoid chasing)",
            "transit": "Potential breakouts (Set alerts)"
        },
        "Venus": {
            "high": "Harmonious trading (Smooth trends)",
            "low": "Choppy conditions (Reduce size)",
            "transit": "Support/resistance tests likely)"
        },
        "Jupiter": {
            "high": "Expansion phase (Position trades)",
            "low": "Growth stalled (Take profits)",
            "transit": "Major moves possible (Watch volume)"
        }
    }
    
    base_effect = effects.get(planet, {
        "high": "Positive influence (Look for entries)",
        "low": "Negative influence (Consider exits)",
        "transit": "Increased activity (Trade cautiously)"
    })
    
    if in_transit:
        return base_effect["transit"]
    return base_effect["high"] if strength > 0.7 else base_effect["low"] if strength < 0.3 else "Neutral influence (Hold positions)"

def get_planet(symbol: str) -> str:
    """Get planet for symbol"""
    symbol_upper = symbol.upper()
    for key, planet in PLANET_MAPPING.items():
        if key in symbol_upper:
            return planet
    return PLANET_MAPPING["DEFAULT"]

def calculate_signal(strength: float, planet: str, in_transit: bool) -> Tuple[str, str]:
    """Determine trading signal based on planetary position"""
    if in_transit:
        if strength > 0.75:
            return "STRONG_BUY", f"Strong {planet} transit - Excellent entry point"
        elif strength < 0.25:
            return "STRONG_SELL", f"Critical {planet} transit - Exit opportunity"
        return "WARNING", f"{planet} transit - High volatility expected"
    
    if strength > 0.8:
        return "STRONG_BUY", f"Very favorable {planet} alignment"
    elif strength > 0.6:
        return "BUY", f"Positive {planet} influence"
    elif strength < 0.2:
        return "STRONG_SELL", f"Critical {planet} opposition"
    elif strength < 0.4:
        return "SELL", f"Negative {planet} aspects"
    return "HOLD", f"Neutral {planet} influence"

def fetch_market_data(symbol: str, now: datetime) -> Dict:
    """Get all data for a market symbol"""
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
        "next_transits": transits["next_transits"],
        "in_transit": transits["in_transit"],
        "effect": transits["effect"],
        "planet_emoji": PLANET_EMOJIS.get(planet, "🪐")
    }

def fetch_all_markets(symbols: List[str], now: datetime) -> List[Dict]:
    """Fetch data for all markets in parallel"""
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda s: fetch_market_data(s, now), symbols))
        return sorted(results, key=lambda x: x["strength"], reverse=True)

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Global Markets Astro Dashboard",
        layout="wide",
        page_icon="🌎",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .market-card {
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
        .section-title { margin-top: 30px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.title("🌍 Market Controls")
        
        # Symbol selection
        selected_symbols = st.multiselect(
            "Select Markets",
            GLOBAL_SYMBOLS,
            default=GLOBAL_SYMBOLS
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
    st.title("🌐 Global Markets Astro Dashboard")
    st.caption("Real-time planetary analysis for commodities and major indices")
    
    # Create placeholder for dynamic content
    content_placeholder = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            
            # Fetch data
            with st.spinner("Analyzing planetary positions..."):
                market_data = fetch_all_markets(selected_symbols, now)
            
            # Filter data
            filtered_data = [
                d for d in market_data 
                if (d["strength"] >= min_confidence/100) and 
                (d["signal"] in signal_filter)
            ]
            
            # Display in placeholder
            with content_placeholder.container():
                # Current Planetary Status
                st.markdown("### 🌠 Current Planetary Positions")
                
                # Get unique planets
                planet_status = {}
                for data in market_data:
                    if data["planet"] not in planet_status:
                        planet_status[data["planet"]] = {
                            "emoji": data["planet_emoji"],
                            "strength": data["strength"],
                            "in_transit": data["in_transit"],
                            "next_transit": data["next_transits"][0]
                        }
                
                # Display planet cards
                cols = st.columns(len(planet_status))
                for i, (planet, info) in enumerate(planet_status.items()):
                    with cols[i % len(cols)]:
                        transit_class = "transit-active" if info["in_transit"] else ""
                        st.markdown(f"""
                        <div class="market-card {transit_class}">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="font-size:1.5rem">{info['emoji']}</span>
                                <h3>{planet}</h3>
                            </div>
                            <p>Strength: {info['strength']:.0%}</p>
                            <p>Status: {'In Transit' if info['in_transit'] else 'Normal'}</p>
                            <p>Next Transit: {info['next_transit'].strftime('%H:%M UTC')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Active Market Signals
                st.markdown("### 📊 Active Market Signals")
                
                if not filtered_data:
                    st.warning("No strong signals at current confidence level")
                else:
                    # Group by signal type
                    signal_groups = {sig: [] for sig in EYE_SYMBOLS.keys()}
                    for data in filtered_data:
                        signal_groups[data["signal"]].append(data)
                    
                    for signal_type, signals in signal_groups.items():
                        if signals:
                            st.markdown(f"#### {EYE_SYMBOLS[signal_type]} {signal_type.replace('_', ' ')} Signals")
                            
                            num_cols = min(4, max(2, 6 - len(signals)//3))
                            cols = st.columns(num_cols)
                            
                            for i, data in enumerate(signals):
                                with cols[i % num_cols]:
                                    card_class = signal_type.lower().replace("_", "-")
                                    price_display = f"{data['price']:,.2f}" if data['price'] > 0 else "N/A"
                                    st.markdown(f"""
                                    <div class="market-card {card_class}">
                                        <div style="display:flex; align-items:center; gap:10px;">
                                            <span style="font-size:1.2rem">{data['planet_emoji']}</span>
                                            <h4>{data['symbol']}</h4>
                                        </div>
                                        <p>Price: <span class="price-{'up' if data['strength'] > 0.7 else 'down' if data['strength'] < 0.3 else 'neutral'}">{price_display}</span></p>
                                        <p><strong>{EYE_SYMBOLS[data['signal']]} {data['signal'].replace('_', ' ')}</strong></p>
                                        <p>Confidence: {data['strength']:.0%}</p>
                                        <small>{data['reason']}</small>
                                        <div style="margin-top:10px; padding:8px; background:#f8f9fa; border-radius:5px;">
                                            <small>Next Transit: {data['next_transits'][0].strftime('%H:%M UTC')}</small>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                
                # Upcoming Transit Schedule
                st.markdown("### ⏳ Upcoming Planetary Transits (Next 12 Hours)")
                
                # Collect all upcoming transits
                upcoming_transits = []
                for data in market_data:
                    for transit in data["next_transits"]:
                        if (transit - now).total_seconds() < 12*3600:
                            upcoming_transits.append({
                                "time": transit,
                                "planet": data["planet"],
                                "symbol": data["symbol"],
                                "emoji": data["planet_emoji"]
                            })
                
                if upcoming_transits:
                    # Sort by time and group by planet
                    upcoming_transits.sort(key=lambda x: x["time"])
                    
                    # Display in timeline
                    for transit in upcoming_transits:
                        time_diff = (transit["time"] - now).total_seconds()/3600
                        st.markdown(f"""
                        <div class="market-card">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="font-size:1.2rem">{transit['emoji']}</span>
                                <div>
                                    <strong>{transit['planet']} Transit</strong>
                                    <p>{transit['symbol']} in {time_diff:.1f} hours</p>
                                    <small>{transit['time'].strftime('%H:%M UTC')}</small>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No significant planetary transits in next 12 hours")
                
                # Footer with performance info
                st.markdown("---")
                st.caption(f"""
                Last update: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | 
                Processed {len(selected_symbols)} markets in {time.time()-start_time:.2f}s | 
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
