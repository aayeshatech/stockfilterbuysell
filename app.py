import swisseph as swe
from datetime import datetime, timedelta
import pytz
import requests
import os
from time import sleep
import streamlit as st
import pandas as pd

# Configuration
EPHE_PATH = 'C:/Users/a/Downloads/swisseph-master (1)/swisseph-master/ephe'

# Initialize Swiss Ephemeris
swe.set_ephe_path(EPHE_PATH)

# Planetary associations with sectors (simplified)
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

def get_planet_position(planet, date_utc):
    """Get planet's longitude position for a given date"""
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
    return pos[0]  # longitude

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
            
            # Simple aspect detection (conjunction only in this example)
            if abs((current_pos - natal_pos) % 360) <= 3:
                if planet in ['JUPITER', 'VENUS', 'MOON']:
                    alerts.append({
                        'symbol': symbol,
                        'signal': 'BUY',
                        'planet': planet,
                        'reason': f"Benefic {planet} transit",
                        'time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
                elif planet in ['SATURN', 'MARS', 'RAHU', 'KETU']:
                    alerts.append({
                        'symbol': symbol,
                        'signal': 'SELL',
                        'planet': planet,
                        'reason': f"Challenging {planet} transit",
                        'time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
                elif planet == 'SUN':
                    alerts.append({
                        'symbol': symbol,
                        'signal': 'HOLD',
                        'planet': planet,
                        'reason': f"Solar influence on {symbol}",
                        'time': now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                    })
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return alerts

def send_telegram_alert(alert, bot_token, chat_id):
    """Send alert to Telegram"""
    emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '🟡'
    }.get(alert['signal'], '⚪')
    
    message = (
        f"{emoji} <b>{alert['signal']} {alert['symbol']}</b>\n"
        f"Planet: {alert['planet']}\n"
        f"Reason: {alert['reason']}\n"
        f"Time: {alert['time']}"
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
        content = uploaded_file.getvalue().decode("utf-8")
        file_symbols = [s.strip() for s in content.split(',') if s.strip()]
        symbols.update(file_symbols)
    return list(symbols)

def main():
    st.title("Planetary Transit Stock Alert System")
    st.write("Upload your symbol files and configure alerts")
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Upload your symbol files (CSV/TXT)", 
        type=['txt', 'csv'],
        accept_multiple_files=True
    )
    
    # Telegram configuration
    with st.expander("Telegram Alert Configuration"):
        bot_token = st.text_input("Telegram Bot Token", type="password")
        chat_id = st.text_input("Telegram Chat ID")
        test_alert = st.button("Send Test Alert")
        
        if test_alert and bot_token and chat_id:
            test_result = send_telegram_alert({
                'symbol': 'TEST',
                'signal': 'HOLD',
                'planet': 'SUN',
                'reason': 'Test alert',
                'time': datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            }, bot_token, chat_id)
            if test_result:
                st.success("Test alert sent successfully!")
    
    # Analysis controls
    if uploaded_files:
        symbols = process_uploaded_files(uploaded_files)
        st.success(f"Loaded {len(symbols)} unique symbols")
        
        if st.button("Run Analysis Now"):
            with st.spinner("Analyzing planetary transits..."):
                alerts = analyze_transits(symbols)
                
                if alerts:
                    st.subheader(f"Generated {len(alerts)} Alerts")
                    df = pd.DataFrame(alerts)
                    st.dataframe(df)
                    
                    if bot_token and chat_id:
                        with st.spinner("Sending alerts to Telegram..."):
                            success_count = 0
                            for alert in alerts:
                                if send_telegram_alert(alert, bot_token, chat_id):
                                    success_count += 1
                            st.info(f"Sent {success_count}/{len(alerts)} alerts to Telegram")
                else:
                    st.info("No significant transits detected at this time")
    else:
        st.warning("Please upload symbol files to begin")

if __name__ == "__main__":
    main()
