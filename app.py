import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import math
from typing import Dict, Optional
import pytz

# Try importing optional packages
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    
try:
    import ephem
    EHEM_AVAILABLE = True
except ImportError:
    EHEM_AVAILABLE = False

# Initialize Swiss Ephemeris if available
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
    .price-up {
        color: green;
    }
    .price-down {
        color: red;
    }
    .buy-sell-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .buy-badge {
        background-color: #d4edda;
        color: #155724;
    }
    .sell-badge {
        background-color: #f8d7da;
        color: #721c24;
    }
    .transit-detail {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .aspect-detail {
        font-size: 0.85rem;
        padding: 0.25rem;
        border-left: 3px solid #ddd;
        margin-bottom: 0.25rem;
    }
    .aspect-bullish {
        border-left-color: #2ca02c;
        background-color: #f0fff0;
    }
    .aspect-bearish {
        border-left-color: #d62728;
        background-color: #fff0f0;
    }
    .date-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .report-header {
        font-size: 1.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }
    .sector-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .sector-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .sector-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .sector-name {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .sector-signal {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .bullish-signal {
        background-color: #d4edda;
        color: #155724;
    }
    .bearish-signal {
        background-color: #f8d7da;
        color: #721c24;
    }
    .planetary-effect {
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.5rem;
    }
    .stock-list {
        margin-top: 1rem;
        padding-top: 0.5rem;
        border-top: 1px solid #eee;
    }
    .stock-item {
        display: flex;
        justify-content: space-between;
        padding: 0.25rem 0;
    }
    .stock-name {
        font-weight: 500;
    }
    .stock-signal {
        font-weight: bold;
    }
    .time-slot {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1f77b4;
    }
    .time-slot-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .time-slot-title {
        font-weight: bold;
        font-size: 1.2rem;
        color: #1f77b4;
    }
    .time-slot-signal {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .running-time {
        position: fixed;
        top: 10px;
        right: 10px;
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        z-index: 100;
    }
    .strength-meter {
        height: 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .strength-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease-in-out;
    }
    .strength-bullish {
        background-color: #2ca02c;
    }
    .strength-bearish {
        background-color: #d62728;
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
        'ITC': 'ITC.NS',
        'Sun Pharma': 'SUNPHARMA.NS',
        'Maruti': 'MARUTI.NS',
        'Mahindra': 'M&M.NS',
        'NTPC': 'NTPC.NS',
        'Power Grid': 'POWERGRID.NS',
        'Tata Steel': 'TATASTEEL.NS',
        'Coal India': 'COALINDIA.NS',
        'ONGC': 'ONGC.NS',
        'BPCL': 'BPCL.NS',
        'Hind Unilever': 'HINDUNILVR.NS',
        'Nestle': 'NESTLEIND.NS',
        'Asian Paints': 'ASIANPAINT.NS',
        'Titan': 'TITAN.NS',
        'Bajaj Auto': 'BAJAJ-AUTO.NS',
        'Hero Moto': 'HEROMOTOCO.NS',
        'Dr Reddy': 'DRREDDY.NS',
        'Cipla': 'CIPLA.NS',
        'Divis Lab': 'DIVISLAB.NS'
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
        'ITC': 'FMCG',
        'Sun Pharma': 'Pharma',
        'Maruti': 'Auto',
        'Mahindra': 'Auto',
        'NTPC': 'Power',
        'Power Grid': 'Power',
        'Tata Steel': 'Metals',
        'Coal India': 'Mining',
        'ONGC': 'Oil & Gas',
        'BPCL': 'Oil & Gas',
        'Hind Unilever': 'FMCG',
        'Nestle': 'FMCG',
        'Asian Paints': 'Paints',
        'Titan': 'Jewelry',
        'Bajaj Auto': 'Auto',
        'Hero Moto': 'Auto',
        'Dr Reddy': 'Pharma',
        'Cipla': 'Pharma',
        'Divis Lab': 'Pharma'
    }
    
    return watchlist, sectors

# Define trading time slots
def get_trading_time_slots():
    """Define trading time slots for Indian market"""
    return [
        ("09:15", "10:15"),
        ("10:15", "11:15"),
        ("11:15", "12:15"),
        ("12:15", "13:15"),
        ("13:15", "14:15"),
        ("14:15", "15:30")
    ]

# Simplified planetary position calculation
def calculate_planetary_positions_simplified(date_time):
    """Calculate planetary positions using simplified mathematical formulas"""
    # This is a simplified calculation for demonstration
    # In real applications, use proper ephemeris data
    
    # Reference date (J2000.0)
    ref_date = datetime(2000, 1, 1, 12, 0, 0)
    
    # Days since reference
    days_since_ref = (date_time - ref_date).total_seconds() / 86400.0
    
    # Mean orbital elements (simplified)
    orbital_elements = {
        'Sun': {'period': 365.25636, 'epoch': 0.0, 'ecc': 0.0167},
        'Moon': {'period': 27.32166, 'epoch': 0.0, 'ecc': 0.0549},
        'Mercury': {'period': 87.969, 'epoch': 0.0, 'ecc': 0.2056},
        'Venus': {'period': 224.701, 'epoch': 0.0, 'ecc': 0.0068},
        'Mars': {'period': 686.980, 'epoch': 0.0, 'ecc': 0.0934},
        'Jupiter': {'period': 4332.589, 'epoch': 0.0, 'ecc': 0.0484},
        'Saturn': {'period': 10759.22, 'epoch': 0.0, 'ecc': 0.0539}
    }
    
    positions = {}
    
    for planet, elements in orbital_elements.items():
        # Calculate mean anomaly
        M = (days_since_ref / elements['period']) * 360 + elements['epoch']
        M = M % 360
        
        # Solve Kepler's equation (simplified)
        E = M
        for _ in range(5):  # Newton's method iterations
            E = M + elements['ecc'] * math.sin(math.radians(E))
        
        # Calculate true anomaly
        true_anomaly = 2 * math.degrees(math.atan(math.sqrt((1 + elements['ecc'])/(1 - elements['ecc'])) * math.tan(math.radians(E/2))))
        
        # Add some variation based on time of day
        time_factor = (date_time.hour + date_time.minute/60.0) / 24.0 * 360
        
        # Final position (simplified)
        positions[planet] = (true_anomaly + time_factor) % 360
    
    # Calculate approximate Rahu and Ketu positions
    # These are the lunar nodes, approximately opposite each other
    if 'Moon' in positions:
        # Rahu is approximately 180 degrees from Moon's position
        positions['Rahu'] = (positions['Moon'] + 180) % 360
        # Ketu is opposite to Rahu
        positions['Ketu'] = (positions['Rahu'] + 180) % 360
    
    return positions

# Calculate planetary positions using ephem
def calculate_planetary_positions_ephem(date_time):
    """Calculate planetary positions using ephem library"""
    if not EHEM_AVAILABLE:
        return {}
    
    try:
        # Set up observer
        observer = ephem.Observer()
        observer.date = date_time
        
        # Get planetary positions
        sun = ephem.Sun(observer)
        moon = ephem.Moon(observer)
        mercury = ephem.Mercury(observer)
        venus = ephem.Venus(observer)
        mars = ephem.Mars(observer)
        jupiter = ephem.Jupiter(observer)
        saturn = ephem.Saturn(observer)
        
        # Convert to ecliptic longitude (simplified)
        positions = {
            'Sun': math.degrees(sun.ra) % 360,
            'Moon': math.degrees(moon.ra) % 360,
            'Mercury': math.degrees(mercury.ra) % 360,
            'Venus': math.degrees(venus.ra) % 360,
            'Mars': math.degrees(mars.ra) % 360,
            'Jupiter': math.degrees(jupiter.ra) % 360,
            'Saturn': math.degrees(saturn.ra) % 360
        }
        
        # Calculate approximate Rahu and Ketu
        positions['Rahu'] = (positions['Moon'] + 180) % 360
        positions['Ketu'] = (positions['Rahu'] + 180) % 360
        
        return positions
    except Exception as e:
        st.error(f"Ephem calculation failed: {str(e)}")
        return {}

# Calculate planetary positions using Swiss Ephemeris
def calculate_planetary_positions_swisseph(date_time):
    """Calculate planetary positions using Swiss Ephemeris"""
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
        st.error(f"Swiss Ephemeris calculation failed: {str(e)}")
        return {}

# Main function to get planetary positions with fallback
def calculate_planetary_positions(date_time):
    """Calculate planetary positions with multiple fallback methods"""
    # Try Swiss Ephemeris first
    positions = calculate_planetary_positions_swisseph(date_time)
    if positions:
        return positions
    
    # Try ephem
    positions = calculate_planetary_positions_ephem(date_time)
    if positions:
        return positions
    
    # Fall back to simplified calculation
    st.warning("Using simplified planetary calculations")
    positions = calculate_planetary_positions_simplified(date_time)
    
    return positions

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
        },
        'Auto': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Pharma': {
            'bullish': [('Jupiter', 'any', 'Trine'), ('Venus', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Metals': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Power': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Oil & Gas': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'FMCG': {
            'bullish': [('Venus', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Paints': {
            'bullish': [('Venus', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Jewelry': {
            'bullish': [('Venus', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Infrastructure': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
            'bearish': [('Saturn', 'any', 'Square'), ('Rahu', 'any', 'Square')]
        },
        'Mining': {
            'bullish': [('Mars', 'any', 'Trine'), ('Jupiter', 'any', 'Trine')],
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
                    'time': current_time.strftime("%H:%M"),
                    'detail': f"{p1} in {aspect_type} with {p2} (Strength: {strength:.2f})"
                })
        
        # Check bearish signals
        for sp1, sp2, stype in bearish_aspects:
            if ((p1 == sp1 and p2 == sp2) or (p1 == sp2 and p2 == sp1)) and \
               (stype == 'any' or aspect_type == stype):
                signals.append({
                    'type': 'bearish',
                    'strength': strength,
                    'reason': f"{p1}-{p2} {aspect_type}",
                    'time': current_time.strftime("%H:%M"),
                    'detail': f"{p1} in {aspect_type} with {p2} (Strength: {strength:.2f})"
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
                        'time': current_time.strftime("%H:%M"),
                        'detail': f"Sector {sector}: {p1} in {aspect_type} with {p2} (Strength: {strength*1.2:.2f})"
                    })
            
            # Sector bearish
            for sp1, stype, satype in sector_rules[sector]['bearish']:
                if (p1 == sp1 or p2 == sp1) and (stype == 'any' or aspect_type == satype):
                    signals.append({
                        'type': 'bearish',
                        'strength': strength * 1.2,  # Boost sector signals
                        'reason': f"{sector}: {p1}-{p2} {aspect_type}",
                        'time': current_time.strftime("%H:%M"),
                        'detail': f"Sector {sector}: {p1} in {aspect_type} with {p2} (Strength: {strength*1.2:.2f})"
                    })
    
    return signals

# Format planetary position
def format_planetary_position(longitude):
    """Format planetary longitude to zodiac sign and degree"""
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
             "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    sign_num = int(longitude / 30)
    sign = signs[sign_num]
    degree = longitude % 30
    minute = (degree - int(degree)) * 60
    return f"{int(degree)}°{int(minute)}' {sign}"

# Format recommendation badge
def format_recommendation_badge(recommendation_class, recommendation):
    """Format recommendation as HTML badge"""
    return f"<span class='buy-sell-badge {recommendation_class}'>{recommendation}</span>"

# Generate intraday report
def generate_intraday_report(selected_date, watchlist, sectors):
    """Generate intraday astrological report for selected date"""
    # Get trading time slots
    time_slots = get_trading_time_slots()
    
    # Generate report for each time slot
    intraday_report = []
    
    for start_time_str, end_time_str in time_slots:
        # Parse time strings
        start_hour, start_minute = map(int, start_time_str.split(':'))
        end_hour, end_minute = map(int, end_time_str.split(':'))
        
        # Create datetime objects for the time slot
        start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
        end_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=end_hour, minutes=end_minute)
        
        # Calculate planetary positions and aspects for the start of the time slot
        positions = calculate_planetary_positions(start_time)
        aspects = calculate_planetary_aspects(positions)
        
        # Generate signals for all symbols
        time_slot_data = {
            'time_slot': f"{start_time_str} - {end_time_str}",
            'start_time': start_time,
            'end_time': end_time,
            'positions': positions,
            'aspects': aspects,
            'symbols': []
        }
        
        # Determine ruling planet for this time slot (simplified)
        # In a real system, this would be based on the day of the week and time
        ruling_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        slot_index = time_slots.index((start_time_str, end_time_str))
        ruling_planet = ruling_planets[slot_index % len(ruling_planets)]
        time_slot_data['ruling_planet'] = ruling_planet
        
        # Generate signals for each symbol
        for symbol, ticker in watchlist.items():
            sector = sectors.get(symbol, 'Unknown')
            
            # Generate signals
            signals = generate_trading_signals(aspects, symbol, sector, start_time)
            
            # Calculate overall signal
            bullish_strength = sum(s['strength'] for s in signals if s['type'] == 'bullish')
            bearish_strength = sum(s['strength'] for s in signals if s['type'] == 'bearish')
            
            # Determine buy/sell recommendation (only BUY or SELL)
            if bullish_strength > bearish_strength:
                recommendation = "BUY"
                recommendation_class = "buy-badge"
            else:
                recommendation = "SELL"
                recommendation_class = "sell-badge"
            
            if bullish_strength > bearish_strength:
                overall_signal = "🐂 Bullish"
                signal_class = "signal-bullish"
            elif bearish_strength > bullish_strength:
                overall_signal = "🐻 Bearish"
                signal_class = "signal-bearish"
            else:
                overall_signal = "⚖ Neutral"
                signal_class = "signal-neutral"
            
            time_slot_data['symbols'].append({
                'Symbol': symbol,
                'Sector': sector,
                'Signal': overall_signal,
                'Signal Class': signal_class,
                'Recommendation': recommendation,
                'Recommendation Class': recommendation_class,
                'Bullish Strength': round(bullish_strength, 2),
                'Bearish Strength': round(bearish_strength, 2),
                'Recent Signals': ", ".join([s['reason'] for s in signals[:3]]),
                'Signals': signals,
                'Transit Details': [s['detail'] for s in signals]
            })
        
        intraday_report.append(time_slot_data)
    
    return intraday_report

# Generate sector analysis for intraday report
def generate_intraday_sector_analysis(intraday_report):
    """Generate sector-level analysis for intraday report"""
    sector_analysis = {}
    
    # Initialize sector analysis
    for time_slot in intraday_report:
        for symbol_data in time_slot['symbols']:
            sector = symbol_data['Sector']
            if sector not in sector_analysis:
                sector_analysis[sector] = {
                    'time_slots': {},
                    'overall_bullish': 0,
                    'overall_bearish': 0
                }
            
            time_slot_key = time_slot['time_slot']
            if time_slot_key not in sector_analysis[sector]['time_slots']:
                sector_analysis[sector]['time_slots'][time_slot_key] = {
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'bullish_strength': 0,
                    'bearish_strength': 0,
                    'planetary_effects': []
                }
            
            # Add symbol data to sector analysis
            if symbol_data['Signal'] == '🐂 Bullish':
                sector_analysis[sector]['time_slots'][time_slot_key]['bullish_count'] += 1
                sector_analysis[sector]['time_slots'][time_slot_key]['bullish_strength'] += symbol_data['Bullish Strength']
                sector_analysis[sector]['overall_bullish'] += 1
            elif symbol_data['Signal'] == '🐻 Bearish':
                sector_analysis[sector]['time_slots'][time_slot_key]['bearish_count'] += 1
                sector_analysis[sector]['time_slots'][time_slot_key]['bearish_strength'] += symbol_data['Bearish Strength']
                sector_analysis[sector]['overall_bearish'] += 1
            
            # Add planetary effects
            for signal in symbol_data['Signals']:
                if 'Sector:' in signal['reason']:
                    sector_analysis[sector]['time_slots'][time_slot_key]['planetary_effects'].append({
                        'planets': signal['reason'].split(': ')[1],
                        'type': signal['type'],
                        'strength': signal['strength']
                    })
    
    return sector_analysis

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🌌 Planetary Transit Trading Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:gray;">Astrological analysis for trading decisions</p>', unsafe_allow_html=True)
    
    # Display running time
    current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")
    st.markdown(f'<div class="running-time">Current Time: {current_time}</div>', unsafe_allow_html=True)
    
    # Load watchlist
    watchlist, sectors = load_watchlist()
    
    # Date selection section
    st.markdown('<div class="date-selector">', unsafe_allow_html=True)
    st.subheader("📅 Select Date for Analysis")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            min_value=datetime(2000, 1, 1),
            max_value=datetime.now().date() + timedelta(days=365)
        )
    
    with col2:
        st.markdown("###")
        if st.button("Generate Daily Report", type="primary"):
            st.session_state.report_generated = True
            st.session_state.selected_date = selected_date
            st.rerun()
    
    with col3:
        st.markdown("###")
        if st.button("Use Current Date"):
            st.session_state.selected_date = datetime.now().date()
            st.session_state.report_generated = True
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    if 'expanded_sectors' not in st.session_state:
        st.session_state.expanded_sectors = set()
    
    # Generate report if date is selected
    if st.session_state.report_generated:
        selected_date = st.session_state.selected_date
        
        # Display report header
        report_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")
        st.markdown(f'<div class="report-header">📊 Daily Astrological Report for {selected_date.strftime("%B %d, %Y")} (Generated at {report_time})</div>', unsafe_allow_html=True)
        
        # Generate intraday report
        with st.spinner("Generating intraday astrological report..."):
            intraday_report = generate_intraday_report(selected_date, watchlist, sectors)
        
        # Generate sector analysis
        sector_analysis = generate_intraday_sector_analysis(intraday_report)
        
        # Sidebar controls
        st.sidebar.header("Dashboard Controls")
        
        # Sector filter
        all_sectors = list(set(sectors.values()))
        selected_sectors = st.sidebar.multiselect(
            "Filter by Sector",
            options=all_sectors,
            default=all_sectors
        )
        
        # Signal strength filter
        min_strength = st.sidebar.slider("Minimum Signal Strength", 0.1, 1.0, 0.5)
        
        # Symbol search
        search_term = st.sidebar.text_input("Search Symbol", "")
        
        # Main content area
        st.header("Intraday Astrological Analysis")
        
        # Display time slots
        for time_slot in intraday_report:
            time_slot_str = time_slot['time_slot']
            ruling_planet = time_slot['ruling_planet']
            
            # Calculate overall signal for the time slot
            bullish_count = sum(1 for s in time_slot['symbols'] if s['Signal'] == '🐂 Bullish')
            bearish_count = sum(1 for s in time_slot['symbols'] if s['Signal'] == '🐻 Bearish')
            
            if bullish_count > bearish_count:
                overall_signal = "Bullish"
                signal_class = "bullish-signal"
            else:
                overall_signal = "Bearish"
                signal_class = "bearish-signal"
            
            # Display time slot section
            st.markdown(f"""
            <div class="time-slot">
                <div class="time-slot-header">
                    <div class="time-slot-title">{time_slot_str} (Ruled by {ruling_planet})</div>
                    <div class="time-slot-signal {signal_class}">{overall_signal}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display planetary positions
            with st.expander(f"Planetary Positions at {time_slot_str.split(' - ')[0]}"):
                if time_slot['positions']:
                    pos_data = []
                    for planet, longitude in time_slot['positions'].items():
                        pos_data.append({
                            'Planet': planet,
                            'Position': format_planetary_position(longitude),
                            'Longitude': round(longitude, 2)
                        })
                    
                    pos_df = pd.DataFrame(pos_data)
                    st.dataframe(pos_df, use_container_width=True)
                else:
                    st.info("Planetary positions not available")
            
            # Display sector analysis for this time slot
            st.subheader(f"Sector Analysis - {time_slot_str}")
            
            # Create columns for sectors
            sector_cols = st.columns(3)
            
            col_idx = 0
            for sector, data in sector_analysis.items():
                if sector not in selected_sectors:
                    continue
                
                if time_slot_str in data['time_slots']:
                    slot_data = data['time_slots'][time_slot_str]
                    
                    # Determine sector signal
                    if slot_data['bullish_strength'] > slot_data['bearish_strength']:
                        sector_signal = "Bullish"
                        signal_class = "bullish-signal"
                    else:
                        sector_signal = "Bearish"
                        signal_class = "bearish-signal"
                    
                    with sector_cols[col_idx % 3]:
                        # Create sector card
                        st.markdown(f"""
                        <div class="sector-card">
                            <div class="sector-header">
                                <div class="sector-name">{sector}</div>
                                <div class="sector-signal {signal_class}">{sector_signal}</div>
                            </div>
                            <div>
                                <strong>Bullish:</strong> {slot_data['bullish_count']} | 
                                <strong>Bearish:</strong> {slot_data['bearish_count']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show strength meters
                        st.markdown("<strong>Bullish Strength:</strong>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="strength-meter">
                            <div class="strength-fill strength-bullish" style="width: {min(slot_data['bullish_strength'] * 100, 100)}%"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"{slot_data['bullish_strength']:.2f}")
                        
                        st.markdown("<strong>Bearish Strength:</strong>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="strength-meter">
                            <div class="strength-fill strength-bearish" style="width: {min(slot_data['bearish_strength'] * 100, 100)}%"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"{slot_data['bearish_strength']:.2f}")
                        
                        # Show planetary effects
                        if slot_data['planetary_effects']:
                            st.markdown("<strong>Planetary Effects:</strong>", unsafe_allow_html=True)
                            for effect in slot_data['planetary_effects']:
                                effect_color = "green" if effect['type'] == 'bullish' else "red"
                                st.markdown(f"""
                                <div class="planetary-effect">
                                    <span style="color: {effect_color}">{effect['planets']}</span> 
                                    (Strength: {effect['strength']:.2f})
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Toggle button for sector details
                        if st.button(f"Show Stocks in {sector}", key=f"toggle_{sector}_{time_slot_str}"):
                            if f"{sector}_{time_slot_str}" in st.session_state.expanded_sectors:
                                st.session_state.expanded_sectors.remove(f"{sector}_{time_slot_str}")
                            else:
                                st.session_state.expanded_sectors.add(f"{sector}_{time_slot_str}")
                            st.rerun()
                        
                        # Show stocks if sector is expanded
                        if f"{sector}_{time_slot_str}" in st.session_state.expanded_sectors:
                            st.markdown(f"<div class='stock-list'>", unsafe_allow_html=True)
                            
                            # Get stocks in this sector for this time slot
                            sector_symbols = [s for s in time_slot['symbols'] if s['Sector'] == sector]
                            
                            # Show bullish stocks
                            bullish_stocks = [s for s in sector_symbols if s['Signal'] == '🐂 Bullish']
                            if bullish_stocks:
                                st.markdown("<div style='color: green; font-weight: bold;'>Bullish Stocks:</div>", unsafe_allow_html=True)
                                for stock in bullish_stocks:
                                    st.markdown(f"""
                                    <div class="stock-item">
                                        <div class="stock-name">{stock['Symbol']}</div>
                                        <div class="stock-signal" style="color: green;">BUY</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Show bearish stocks
                            bearish_stocks = [s for s in sector_symbols if s['Signal'] == '🐻 Bearish']
                            if bearish_stocks:
                                st.markdown("<div style='color: red; font-weight: bold;'>Bearish Stocks:</div>", unsafe_allow_html=True)
                                for stock in bearish_stocks:
                                    st.markdown(f"""
                                    <div class="stock-item">
                                        <div class="stock-name">{stock['Symbol']}</div>
                                        <div class="stock-signal" style="color: red;">SELL</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    col_idx += 1
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed transit information section
        st.header("Detailed Astrological Analysis")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Symbol Details", "All Aspects", "Summary"])
        
        with tab1:
            st.subheader("Symbol-wise Astrological Analysis")
            
            # Symbol selector
            all_symbols = [s['Symbol'] for time_slot in intraday_report for s in time_slot['symbols']]
            symbol_options = list(set(all_symbols))
            
            if symbol_options:
                selected_symbol = st.selectbox("Select Symbol for Detailed Analysis", options=symbol_options)
                
                if selected_symbol:
                    # Find all time slots for this symbol
                    symbol_time_slots = []
                    for time_slot in intraday_report:
                        for symbol_data in time_slot['symbols']:
                            if symbol_data['Symbol'] == selected_symbol:
                                symbol_time_slots.append({
                                    'time_slot': time_slot['time_slot'],
                                    'data': symbol_data
                                })
                    
                    # Display symbol details for each time slot
                    for slot in symbol_time_slots:
                        st.markdown(f"### {slot['time_slot']}")
                        
                        # Display symbol details
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Symbol:** {selected_symbol}")
                            st.markdown(f"**Sector:** {slot['data']['Sector']}")
                            st.markdown(f"**Signal:** <span class='{slot['data']['Signal Class']}'>{slot['data']['Signal']}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Recommendation:** {format_recommendation_badge(slot['data']['Recommendation Class'], slot['data']['Recommendation'])}", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("### Signal Strength")
                            st.markdown(f"**Bullish Strength:** {slot['data']['Bullish Strength']}")
                            st.markdown(f"**Bearish Strength:** {slot['data']['Bearish Strength']}")
                            
                            # Signal strength bars
                            st.progress(slot['data']['Bullish Strength'] / max(slot['data']['Bullish Strength'] + slot['data']['Bearish Strength'], 0.001))
                            st.markdown(f"<span style='color: green'>Bullish: {slot['data']['Bullish Strength']:.2f}</span>", unsafe_allow_html=True)
                            st.progress(slot['data']['Bearish Strength'] / max(slot['data']['Bullish Strength'] + slot['data']['Bearish Strength'], 0.001))
                            st.markdown(f"<span style='color: red'>Bearish: {slot['data']['Bearish Strength']:.2f}</span>", unsafe_allow_html=True)
                        
                        # Display transit details
                        st.markdown("### Active Transits")
                        if slot['data']['Transit Details']:
                            for detail in slot['data']['Transit Details']:
                                st.markdown(f"<div class='transit-detail'>🔮 {detail}</div>", unsafe_allow_html=True)
                        else:
                            st.info("No significant transits affecting this symbol at this time")
                        
                        st.markdown("---")
            else:
                st.info("No symbols found for selected filters")
        
        with tab2:
            st.subheader("All Planetary Aspects")
            
            # Collect all aspects from all time slots
            all_aspects = []
            for time_slot in intraday_report:
                for aspect in time_slot['aspects']:
                    aspect['time_slot'] = time_slot['time_slot']
                    all_aspects.append(aspect)
            
            if all_aspects:
                # Create detailed aspects table
                aspect_details = []
                for aspect in all_aspects:
                    aspect_details.append({
                        'Time Slot': aspect['time_slot'],
                        'Planet 1': aspect['planet1'],
                        'Planet 2': aspect['planet2'],
                        'Aspect': aspect['aspect'],
                        'Angle': f"{aspect['angle']:.1f}°",
                        'Strength': aspect['strength'],
                        'Orb': f"{aspect['orb_used']:.1f}°",
                        'Type': 'Bullish' if aspect['strength'] > 0.7 else 'Bearish' if aspect['strength'] < 0.3 else 'Neutral'
                    })
                
                aspect_df = pd.DataFrame(aspect_details)
                aspect_df = aspect_df.sort_values(['Time Slot', 'Strength'], ascending=[True, False])
                
                # Color code the type column
                def highlight_type(val):
                    color = 'green' if val == 'Bullish' else 'red' if val == 'Bearish' else 'gray'
                    return f'color: {color}'
                
                st.dataframe(
                    aspect_df.style.applymap(highlight_type, subset=['Type']),
                    use_container_width=True
                )
            else:
                st.info("No significant aspects at this time")
        
        with tab3:
            st.subheader("Summary Report")
            
            # Overall market analysis
            st.markdown("### Overall Market Analysis")
            
            # Count recommendations across all time slots
            buy_count = 0
            sell_count = 0
            
            for time_slot in intraday_report:
                for symbol_data in time_slot['symbols']:
                    if symbol_data['Recommendation'] == 'BUY':
                        buy_count += 1
                    elif symbol_data['Recommendation'] == 'SELL':
                        sell_count += 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("BUY Signals", buy_count)
            with col2:
                st.metric("SELL Signals", sell_count)
            
            # Top bullish and bearish symbols
            st.markdown("### Top Signals")
            
            # Calculate average signal strength for each symbol
            symbol_strength = {}
            for time_slot in intraday_report:
                for symbol_data in time_slot['symbols']:
                    symbol = symbol_data['Symbol']
                    if symbol not in symbol_strength:
                        symbol_strength[symbol] = {
                            'bullish': 0,
                            'bearish': 0,
                            'sector': symbol_data['Sector']
                        }
                    
                    if symbol_data['Signal'] == '🐂 Bullish':
                        symbol_strength[symbol]['bullish'] += symbol_data['Bullish Strength']
                    elif symbol_data['Signal'] == '🐻 Bearish':
                        symbol_strength[symbol]['bearish'] += symbol_data['Bearish Strength']
            
            # Calculate average strengths
            for symbol in symbol_strength:
                total_strength = symbol_strength[symbol]['bullish'] + symbol_strength[symbol]['bearish']
                if total_strength > 0:
                    symbol_strength[symbol]['bullish_avg'] = symbol_strength[symbol]['bullish'] / total_strength
                    symbol_strength[symbol]['bearish_avg'] = symbol_strength[symbol]['bearish'] / total_strength
                else:
                    symbol_strength[symbol]['bullish_avg'] = 0
                    symbol_strength[symbol]['bearish_avg'] = 0
            
            # Get top bullish and bearish symbols
            top_bullish = sorted(symbol_strength.items(), key=lambda x: x[1]['bullish_avg'], reverse=True)[:5]
            top_bearish = sorted(symbol_strength.items(), key=lambda x: x[1]['bearish_avg'], reverse=True)[:5]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top Bullish Signals")
                for symbol, data in top_bullish:
                    st.markdown(f"- **{symbol}** ({data['sector']}) - Avg Strength: {data['bullish_avg']:.2f}")
            
            with col2:
                st.markdown("#### Top Bearish Signals")
                for symbol, data in top_bearish:
                    st.markdown(f"- **{symbol}** ({data['sector']}) - Avg Strength: {data['bearish_avg']:.2f}")
            
            # Sector-wise breakdown
            st.markdown("### Sector-wise Breakdown")
            
            sector_breakdown = {}
            for sector in selected_sectors:
                sector_buy = 0
                sector_sell = 0
                
                for time_slot in intraday_report:
                    for symbol_data in time_slot['symbols']:
                        if symbol_data['Sector'] == sector:
                            if symbol_data['Recommendation'] == 'BUY':
                                sector_buy += 1
                            elif symbol_data['Recommendation'] == 'SELL':
                                sector_sell += 1
                
                if sector_buy > 0 or sector_sell > 0:
                    sector_breakdown[sector] = {
                        'BUY': sector_buy,
                        'SELL': sector_sell,
                        'Total': sector_buy + sector_sell
                    }
            
            if sector_breakdown:
                breakdown_df = pd.DataFrame.from_dict(sector_breakdown, orient='index')
                st.dataframe(breakdown_df, use_container_width=True)
    else:
        # Show instructions when no report is generated
        st.info("👆 Please select a date and click 'Generate Daily Report' to view the astrological analysis")

if __name__ == "__main__":
    main()
