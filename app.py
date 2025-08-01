import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import time
import os

# Check if swisseph is available, provide fallback
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    st.warning("Swiss Ephemeris not available - running in demo mode")

# Configuration
EPHE_PATH = './ephe'  # Default path for ephemeris files

# Planetary associations with sectors
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

def setup_swisseph():
    """Initialize Swiss Ephemeris if available"""
    if SWISSEPH_AVAILABLE:
        try:
            swe.set_ephe_path(EPHE_PATH)
            return True
        except Exception as e:
            st.error(f"Error initializing Swiss Ephemeris: {e}")
            return False
    return False

def get_planet_position(planet, date_utc):
    """Get planet's longitude position (or simulated if SwissEph not available)"""
    if not SWISSEPH_AVAILABLE:
        # Fallback simulation for demo purposes
        return (date_utc.hour * 15 + date_utc.minute * 0.25) % 360  # Simulated position
    
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
    """Determine which planet rules a given symbol"""
    symbol_upper = symbol.upper()
    for planet, keywords in PLANETARY_RULES.items():
        for keyword in keywords:
            if keyword in symbol_upper:
                return planet
    return None

def analyze_transits(symbols):
    """Analyze planetary transits for given symbols"""
    now_utc = datetime.now(pytz.utc)
    alerts = []
    
    for symbol in symbols:
        planet = get_planet_for_symbol(symbol)
        if not planet:
            continue
            
        try:
            current_pos = get_planet_position(planet, now_utc)
            natal_pos = current_pos  # In production, use actual natal positions
            
            # Simple aspect detection
            if abs((current_pos - natal_pos) % 360) <= 3:
                if planet in ['JUPITER', 'VENUS', 'MOON']:
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'BUY',
                        'Planet': planet,
                        'Reason': f"Benefic {planet} transit",
                        'Time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
                elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'SELL',
                        'Planet': planet,
                        'Reason': f"Challenging {planet} transit",
                        'Time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
                elif planet == 'SUN':
                    alerts.append({
                        'Symbol': symbol,
                        'Signal': 'HOLD',
                        'Planet': planet,
                        'Reason': f"Solar influence on {symbol}",
                        'Time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return alerts

def send_telegram_alert(alert, bot_token, chat_id):
    """Send alert to Telegram"""
    emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '🟡'
    }.get(alert['Signal'], '⚪')
    
    message = (
        f"{emoji} <b>{alert['Signal']} {alert['Symbol']}</b>\n"
        f"Planet: {alert['Planet']}\n"
        f"Reason: {alert['Reason']}\n"
        f"Time: {alert['Time']}"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to send Telegram alert: {str(e)}")
        return False

def process_uploaded_files(uploaded_files):
    """Process uploaded files to extract symbols"""
    symbols = set()
    for uploaded_file in uploaded_files:
        try:
            content = uploaded_file.getvalue().decode("utf-8")
            file_symbols = [s.strip() for s in content.split(',') if s.strip()]
            symbols.update(file_symbols)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    return list(symbols)

def main():
    st.set_page_config(
        page_title="Planetary Transit Alerts",
        page_icon="✨",
        layout="wide"
    )
    
    st.title("📈 Planetary Transit Stock Alert System")
    st.write("Analyze stock symbols based on planetary transits")
    
    # Initialize Swiss Ephemeris
    if SWISSEPH_AVAILABLE:
        setup_swisseph()
    
    # File upload section
    with st.expander("📤 Upload Symbol Files", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload your symbol files (CSV/TXT)", 
            type=['txt', 'csv'],
            accept_multiple_files=True,
            help="Upload files containing comma-separated stock symbols"
        )
    
    # Telegram configuration
    with st.expander("⚙️ Telegram Configuration"):
        bot_token = st.text_input("Bot Token", type="password", help="Get from @BotFather")
        chat_id = st.text_input("Chat ID", help="Get from @getidsbot")
        
        if st.button("Test Telegram Connection"):
            if not bot_token or not chat_id:
                st.warning("Please enter both Bot Token and Chat ID")
            else:
                test_result = send_telegram_alert({
                    'Symbol': 'TEST',
                    'Signal': 'HOLD',
                    'Planet': 'SUN',
                    'Reason': 'Test alert',
                    'Time': datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                }, bot_token, chat_id)
                if test_result:
                    st.success("✅ Test alert sent successfully!")
    
    # Analysis section
    if uploaded_files:
        symbols = process_uploaded_files(uploaded_files)
        st.success(f"📊 Loaded {len(symbols)} unique symbols")
        
        if st.button("🚀 Run Analysis Now"):
            with st.spinner("🔭 Analyzing planetary transits..."):
                alerts = analyze_transits(symbols)
                
                if alerts:
                    st.subheader(f"📢 Generated {len(alerts)} Alerts")
                    df = pd.DataFrame(alerts)
                    
                    # Display alerts in expandable sections by signal type
                    for signal_type in ['BUY', 'SELL', 'HOLD']:
                        signal_alerts = df[df['Signal'] == signal_type]
                        if not signal_alerts.empty:
                            with st.expander(f"{signal_type} Signals ({len(signal_alerts)})"):
                                st.dataframe(
                                    signal_alerts,
                                    column_config={
                                        "Time": st.column_config.DatetimeColumn(
                                            "Time",
                                            format="YYYY-MM-DD HH:mm:ss UTC"
                                        )
                                    },
                                    use_container_width=True
                                )
                    
                    # Telegram alerts
                    if bot_token and chat_id:
                        with st.spinner(f"📤 Sending {len(alerts)} alerts to Telegram..."):
                            success_count = 0
                            for _, alert in df.iterrows():
                                if send_telegram_alert(alert, bot_token, chat_id):
                                    success_count += 1
                            st.info(f"📨 Sent {success_count}/{len(alerts)} alerts to Telegram")
                else:
                    st.info("🌌 No significant transits detected at this time")
    else:
        st.warning("📂 Please upload symbol files to begin analysis")

if __name__ == "__main__":
    main()
