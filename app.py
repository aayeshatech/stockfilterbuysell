"""Global Markets Astro Dashboard with Color-Coded Transit Signals"""

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

# ================== GLOBAL MARKETS CONFIG ==================
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
    "GC=F": "Sun", "SI=F": "Moon", "CL=F": "Mars", "NG=F": "Venus",
    "BTC-USD": "Uranus", "^DJI": "Jupiter", "^GSPC": "Saturn", "^IXIC": "Mercury"
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
    """Get live market price"""
    try:
        clean_symbol = symbol.replace("^", "").replace("=F", "")
        data = yf.Ticker(clean_symbol).history(period="1d", interval="1m", timeout=5)
        return float(data["Close"].iloc[-1]) if not data.empty else 0.0
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=128)
def get_planet_transits(planet: str, timestamp: float) -> Dict:
    """Calculate planetary transits and strengths"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        
        planet_obj.compute(observer)
        current_strength = float(planet_obj.alt / (ephem.pi/2))
        
        # Calculate next 3 transits
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
    """Get market effect description"""
    effects = {
        "Sun": {"high": "Bullish", "low": "Caution", "transit": "Volatile"},
        "Moon": {"high": "Active", "low": "Uncertain", "transit": "Reversals"},
        "Mars": {"high": "Strong", "low": "Weak", "transit": "Breakouts"},
        "Venus": {"high": "Smooth", "low": "Choppy", "transit": "Tests"},
        "Jupiter": {"high": "Expanding", "low": "Stalled", "transit": "Moves"},
        "Saturn": {"high": "Stable", "low": "Restrictive", "transit": "Pressure"},
        "Mercury": {"high": "Clear", "low": "Confused", "transit": "Changes"},
        "Uranus": {"high": "Innovative", "low": "Stuck", "transit": "Shifts"}
    }
    
    base = effects.get(planet, {"high": "Positive", "low": "Negative", "transit": "Active"})
    return base["transit"] if in_transit else base["high"] if strength > 0.7 else base["low"] if strength < 0.3 else "Neutral"

def get_planet(symbol: str) -> str:
    """Get planet for symbol"""
    return PLANET_MAPPING.get(symbol, "Sun")

def calculate_signal(strength: float, planet: str, in_transit: bool) -> Tuple[str, str]:
    """Determine trading signal"""
    if in_transit:
        if strength > 0.75: return "STRONG_BUY", f"Strong {planet} transit - Buy"
        elif strength < 0.25: return "STRONG_SELL", f"Critical {planet} transit - Sell"
        return "WARNING", f"{planet} transit - Caution"
    
    if strength > 0.8: return "STRONG_BUY", f"Favorable {planet} - Strong Buy"
    elif strength > 0.6: return "BUY", f"Positive {planet} - Buy"
    elif strength < 0.2: return "STRONG_SELL", f"Negative {planet} - Strong Sell"
    elif strength < 0.4: return "SELL", f"Challenging {planet} - Sell"
    return "HOLD", f"Neutral {planet} - Hold"

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
        "planet_emoji": PLANET_EMOJIS.get(planet, "🪐"),
        "signal_color": "green" if "BUY" in signal else "red" if "SELL" in signal else "gray"
    }

def fetch_all_markets(symbols: List[str], now: datetime) -> List[Dict]:
    """Fetch data for all markets"""
    with ThreadPoolExecutor(max_workers=8) as executor:
        return list(executor.map(lambda s: fetch_market_data(s, now), symbols))

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Global Astro Trader",
        layout="wide",
        page_icon="🌐",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .market-card {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid;
        }
        .signal-buy { border-color: #00cc00; background-color: #e6ffe6; }
        .signal-sell { border-color: #cc0000; background-color: #ffe6e6; }
        .signal-hold { border-color: #666666; background-color: #f5f5f5; }
        .transit-timeline {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        .transit-item {
            padding: 8px;
            margin: 4px 0;
            border-radius: 6px;
            border-left: 4px solid;
        }
        .buy-transit { border-color: #00aa00; background-color: #f0fff0; }
        .sell-transit { border-color: #aa0000; background-color: #fff0f0; }
        .neutral-transit { border-color: #666666; background-color: #f8f8f8; }
        .planet-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.title("🌍 Market Controls")
        selected_symbols = st.multiselect(
            "Select Markets", 
            GLOBAL_SYMBOLS,
            default=GLOBAL_SYMBOLS
        )
        live_mode = st.checkbox("Live Mode", True)
        refresh_rate = st.selectbox("Refresh (sec)", [15, 30, 60], index=1)
        st.markdown(f"**Last Update:** {datetime.now(pytz.utc).strftime('%H:%M:%S UTC')}")
    
    # Main content
    st.title("🌌 Planetary Trading Signals")
    content = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            market_data = fetch_all_markets(selected_symbols, now)
            
            with content.container():
                # Current Signals
                st.subheader("📈 Active Market Signals")
                cols = st.columns(4)
                for i, data in enumerate(market_data):
                    with cols[i % 4]:
                        signal_class = f"signal-{data['signal'].lower().replace('strong_', '').replace('_', '-')}"
                        price_display = f"{data['price']:,.2f}" if data['price'] > 0 else "N/A"
                        st.markdown(f"""
                        <div class="market-card {signal_class}">
                            <div class="planet-header">
                                <span style="font-size:1.2em">{data['planet_emoji']}</span>
                                <h3>{data['symbol']}</h3>
                            </div>
                            <p><strong>Price:</strong> {price_display}</p>
                            <p><strong style="color:{data['signal_color']}">
                                {EYE_SYMBOLS[data['signal']]} {data['signal'].replace('_', ' ')}
                            </strong></p>
                            <p><small>{data['reason']}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Transit Timeline
                st.subheader("⏳ Planetary Transit Timeline (Next 12 Hours)")
                
                # Collect all upcoming transits with signals
                transit_events = []
                for data in market_data:
                    for transit_time in data["next_transits"]:
                        if (transit_time - now).total_seconds() < 12*3600:
                            # Predict signal at transit time
                            transit_strength = 0.8 if data["strength"] > 0.7 else 0.2 if data["strength"] < 0.3 else 0.5
                            transit_signal, _ = calculate_signal(
                                transit_strength,
                                data["planet"],
                                True
                            )
                            transit_events.append({
                                "time": transit_time,
                                "symbol": data["symbol"],
                                "planet": data["planet"],
                                "emoji": data["planet_emoji"],
                                "signal": transit_signal,
                                "color": "green" if "BUY" in transit_signal else "red" if "SELL" in transit_signal else "gray"
                            })
                
                # Sort and display
                transit_events.sort(key=lambda x: x["time"])
                for event in transit_events:
                    time_diff = (event["time"] - now).total_seconds()/3600
                    transit_class = "buy-transit" if "BUY" in event["signal"] else "sell-transit" if "SELL" in event["signal"] else "neutral-transit"
                    st.markdown(f"""
                    <div class="transit-timeline">
                        <div class="transit-item {transit_class}">
                            <div style="display:flex; justify-content:space-between;">
                                <div>
                                    <strong>{event['symbol']}</strong> - {event['planet']} {event['emoji']}
                                </div>
                                <div>
                                    {event['time'].strftime('%H:%M UTC')}
                                </div>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-top:6px;">
                                <div>
                                    Signal: <strong style="color:{event['color']}">
                                        {EYE_SYMBOLS[event['signal']]} {event['signal'].replace('_', ' ')}
                                    </strong>
                                </div>
                                <div>
                                    In <strong>{time_diff:.1f} hours</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Footer
                st.caption(f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | Processing time: {time.time()-start_time:.2f}s")
            
            if not live_mode: break
            time.sleep(refresh_rate)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        st.error("System error - please refresh")
        st.exception(e)

if __name__ == "__main__":
    main()
