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
    .special-report-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .special-report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .special-report-title {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .special-report-signal {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .transit-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 2rem;
    }
    .transit-table th, .transit-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    .transit-table th {
        background-color: #f2f2f2;
        font-weight: bold;
        color: #333;
    }
    .transit-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .transit-table tr:hover {
        background-color: #f1f1f1;
    }
    .bullish-text {
        color: #2ca02c;
        font-weight: bold;
    }
    .bearish-text {
        color: #d62728;
        font-weight: bold;
    }
    .aspect-highlight {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    .aspect-bullish-highlight {
        background-color: #d4edda;
        color: #155724;
    }
    .aspect-bearish-highlight {
        background-color: #f8d7da;
        color: #721c24;
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

# Define special symbol rules for bullish/bearish signals
def get_special_symbol_rules():
    """Get specific rules for special symbols (Nifty, BankNifty, Gold)"""
    return {
        'Nifty': {
            'bullish': [
                ('Jupiter', 'Venus', 'Trine'),
                ('Jupiter', 'Sun', 'Trine'),
                ('Venus', 'Sun', 'Trine'),
                ('Jupiter', 'Moon', 'Trine'),
                ('Venus', 'Moon', 'Trine'),
                ('Sun', 'Moon', 'Trine')
            ],
            'bearish': [
                ('Saturn', 'Mars', 'Square'),
                ('Saturn', 'Sun', 'Opposition'),
                ('Mars', 'Saturn', 'Square'),
                ('Saturn', 'Moon', 'Square'),
                ('Mars', 'Moon', 'Square'),
                ('Rahu', 'Sun', 'Conjunction'),
                ('Rahu', 'Moon', 'Conjunction'),
                ('Ketu', 'Sun', 'Conjunction'),
                ('Ketu', 'Moon', 'Conjunction')
            ]
        },
        'BankNifty': {
            'bullish': [
                ('Jupiter', 'Venus', 'Trine'),
                ('Jupiter', 'Mercury', 'Trine'),
                ('Venus', 'Mercury', 'Trine'),
                ('Jupiter', 'Moon', 'Trine'),
                ('Venus', 'Moon', 'Trine'),
                ('Mercury', 'Moon', 'Trine')
            ],
            'bearish': [
                ('Saturn', 'Mars', 'Square'),
                ('Saturn', 'Mercury', 'Opposition'),
                ('Mars', 'Saturn', 'Square'),
                ('Saturn', 'Moon', 'Square'),
                ('Mars', 'Moon', 'Square'),
                ('Rahu', 'Mercury', 'Conjunction'),
                ('Rahu', 'Moon', 'Conjunction'),
                ('Ketu', 'Mercury', 'Conjunction'),
                ('Ketu', 'Moon', 'Conjunction')
            ]
        },
        'Gold': {
            'bullish': [
                ('Jupiter', 'Venus', 'Trine'),
                ('Venus', 'Sun', 'Trine'),
                ('Venus', 'Moon', 'Trine'),
                ('Jupiter', 'Moon', 'Trine'),
                ('Sun', 'Moon', 'Trine'),
                ('Venus', 'Jupiter', 'Sextile')
            ],
            'bearish': [
                ('Saturn', 'Venus', 'Square'),
                ('Saturn', 'Sun', 'Opposition'),
                ('Mars', 'Venus', 'Opposition'),
                ('Saturn', 'Moon', 'Square'),
                ('Mars', 'Moon', 'Square'),
                ('Rahu', 'Venus', 'Conjunction'),
                ('Rahu', 'Moon', 'Conjunction'),
                ('Ketu', 'Venus', 'Conjunction'),
                ('Ketu', 'Moon', 'Conjunction')
            ]
        }
    }

# Generate trading signals for special symbols
def generate_special_symbol_signals(aspects, symbol, current_time):
    """Generate bullish/bearish signals for special symbols based on planetary aspects"""
    # Get rules for this symbol
    rules = get_special_symbol_rules()
    symbol_rules = rules.get(symbol, {'bullish': [], 'bearish': []})
    
    bullish_signals = []
    bearish_signals = []
    
    # Check each aspect against the rules
    for aspect in aspects:
        p1, p2, aspect_type = aspect['planet1'], aspect['planet2'], aspect['aspect']
        strength = aspect['strength']
        
        # Check bullish signals
        for bp1, bp2, btype in symbol_rules['bullish']:
            if ((p1 == bp1 and p2 == bp2) or (p1 == bp2 and p2 == bp1)) and \
               (btype == 'any' or aspect_type == btype):
                bullish_signals.append({
                    'planets': f"{p1}-{p2}",
                    'aspect': aspect_type,
                    'strength': strength,
                    'time': current_time.strftime("%H:%M")
                })
        
        # Check bearish signals
        for sp1, sp2, stype in symbol_rules['bearish']:
            if ((p1 == sp1 and p2 == sp2) or (p1 == sp2 and p2 == sp1)) and \
               (stype == 'any' or aspect_type == stype):
                bearish_signals.append({
                    'planets': f"{p1}-{p2}",
                    'aspect': aspect_type,
                    'strength': strength,
                    'time': current_time.strftime("%H:%M")
                })
    
    # Calculate total strength
    total_bullish = sum(s['strength'] for s in bullish_signals)
    total_bearish = sum(s['strength'] for s in bearish_signals)
    
    # Determine signal and strongest aspect
    if total_bullish > total_bearish:
        signal = "Bullish"
        strongest_aspect = max(bullish_signals, key=lambda x: x['strength']) if bullish_signals else None
    else:
        signal = "Bearish"
        strongest_aspect = max(bearish_signals, key=lambda x: x['strength']) if bearish_signals else None
    
    # Format the strongest aspect string
    aspect_str = ""
    if strongest_aspect:
        aspect_str = f"{strongest_aspect['planets']} {strongest_aspect['aspect']}"
    
    return {
        'signal': signal,
        'bullish_strength': round(total_bullish, 2),
        'bearish_strength': round(total_bearish, 2),
        'strongest_aspect': aspect_str,
        'all_aspects': bullish_signals + bearish_signals
    }

# Generate special transit report for Nifty, BankNifty, and Gold
def generate_special_transit_report(selected_date, watchlist, sectors, selected_time_slot=None):
    """Generate special transit report for Nifty, BankNifty, and Gold in table format"""
    # Get trading time slots
    time_slots = get_trading_time_slots()
    
    # If a specific time slot is selected, only generate for that slot
    if selected_time_slot:
        time_slots = [selected_time_slot]
    
    # Special symbols
    special_symbols = ['Nifty', 'BankNifty', 'Gold']
    
    # Create report data
    report_data = []
    
    for start_time_str, end_time_str in time_slots:
        # Parse time strings
        start_hour, start_minute = map(int, start_time_str.split(':'))
        end_hour, end_minute = map(int, end_time_str.split(':'))
        
        # Create datetime objects for the time slot
        start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
        
        # Calculate planetary positions and aspects for the start of the time slot
        positions = calculate_planetary_positions(start_time)
        aspects = calculate_planetary_aspects(positions)
        
        # Generate signals for each special symbol
        for symbol in special_symbols:
            sector = sectors.get(symbol, 'Unknown')
            signal_data = generate_special_symbol_signals(aspects, symbol, start_time)
            
            # Add to report data
            report_data.append({
                'Time Factor': f"{start_time_str} - {end_time_str}",
                'Index Name': symbol,
                'Bullish/Bearish': signal_data['signal'],
                'Time': start_time_str,
                'Planetary Aspect': signal_data['strongest_aspect'],
                'Bullish Strength': signal_data['bullish_strength'],
                'Bearish Strength': signal_data['bearish_strength'],
                'All Aspects': signal_data['all_aspects']
            })
    
    return report_data

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
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Time slot selector
    time_slots = get_trading_time_slots()
    time_slot_options = ["All Time Slots"] + [f"{start} - {end}" for start, end in time_slots]
    selected_time_slot_option = st.sidebar.selectbox(
        "Select Time Slot",
        options=time_slot_options,
        index=0
    )
    
    # Parse selected time slot
    selected_time_slot = None
    if selected_time_slot_option != "All Time Slots":
        start_time_str, end_time_str = selected_time_slot_option.split(" - ")
        selected_time_slot = (start_time_str, end_time_str)
    
    # Symbol selector for detailed view
    selected_symbol = st.sidebar.selectbox(
        "Select Symbol for Detailed View",
        options=["All", "Nifty", "BankNifty", "Gold"]
    )
    
    # Generate report if date is selected
    if st.session_state.report_generated:
        selected_date = st.session_state.selected_date
        
        # Display report header
        report_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")
        st.markdown(f'<div class="report-header">📊 Daily Astrological Report for {selected_date.strftime("%B %d, %Y")} (Generated at {report_time})</div>', unsafe_allow_html=True)
        
        # Generate special transit report
        with st.spinner("Generating special transit report..."):
            special_report_data = generate_special_transit_report(selected_date, watchlist, sectors, selected_time_slot)
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Special Transit Report", "Detailed Analysis"])
        
        with tab1:
            st.header("Special Transit Report: Nifty, BankNifty, Gold")
            
            # Display the transit report table
            if special_report_data:
                # Filter by selected symbol if not "All"
                if selected_symbol != "All":
                    filtered_data = [d for d in special_report_data if d['Index Name'] == selected_symbol]
                else:
                    filtered_data = special_report_data
                
                # Create DataFrame
                report_df = pd.DataFrame(filtered_data)
                
                # Display table with custom styling
                st.markdown("""
                <table class="transit-table">
                    <thead>
                        <tr>
                            <th>Time Factor</th>
                            <th>Index Name</th>
                            <th>Bullish/Bearish</th>
                            <th>Time</th>
                            <th>Planetary Aspect</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in report_df.iterrows():
                    signal_class = "bullish-text" if row['Bullish/Bearish'] == "Bullish" else "bearish-text"
                    aspect_class = "aspect-bullish-highlight" if row['Bullish/Bearish'] == "Bullish" else "aspect-bearish-highlight"
                    
                    st.markdown(f"""
                    <tr>
                        <td>{row['Time Factor']}</td>
                        <td><strong>{row['Index Name']}</strong></td>
                        <td class="{signal_class}">{row['Bullish/Bearish']}</td>
                        <td>{row['Time']}</td>
                        <td><span class="{aspect_class}">{row['Planetary Aspect']}</span></td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                    </tbody>
                </table>
                """, unsafe_allow_html=True)
                
                # Show signal strength summary
                st.subheader("Signal Strength Summary")
                
                # Group by index name
                for symbol in ['Nifty', 'BankNifty', 'Gold']:
                    if selected_symbol != "All" and selected_symbol != symbol:
                        continue
                        
                    symbol_data = report_df[report_df['Index Name'] == symbol]
                    
                    if not symbol_data.empty:
                        avg_bullish = symbol_data['Bullish Strength'].mean()
                        avg_bearish = symbol_data['Bearish Strength'].mean()
                        
                        # Determine overall signal
                        if avg_bullish > avg_bearish:
                            overall_signal = "Bullish"
                            signal_class = "bullish-signal"
                        else:
                            overall_signal = "Bearish"
                            signal_class = "bearish-signal"
                        
                        st.markdown(f"""
                        <div class="special-report-card">
                            <div class="special-report-header">
                                <div class="special-report-title">{symbol}</div>
                                <div class="special-report-signal {signal_class}">{overall_signal}</div>
                            </div>
                            <div>
                                <strong>Avg Bullish Strength:</strong> {avg_bullish:.2f} | 
                                <strong>Avg Bearish Strength:</strong> {avg_bearish:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No transit data available for the selected date and time slot.")
        
        with tab2:
            st.header("Detailed Astrological Analysis")
            
            # Display planetary positions
            st.subheader("Planetary Positions")
            
            # Get the first time slot for planetary positions
            time_slot = selected_time_slot if selected_time_slot else time_slots[0]
            start_time_str, end_time_str = time_slot
            start_hour, start_minute = map(int, start_time_str.split(':'))
            start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
            
            positions = calculate_planetary_positions(start_time)
            
            if positions:
                pos_data = []
                for planet, longitude in positions.items():
                    pos_data.append({
                        'Planet': planet,
                        'Position': format_planetary_position(longitude),
                        'Longitude': round(longitude, 2)
                    })
                
                pos_df = pd.DataFrame(pos_data)
                st.dataframe(pos_df, use_container_width=True)
            else:
                st.info("Planetary positions not available")
            
            # Display planetary aspects
            st.subheader("Planetary Aspects")
            
            aspects = calculate_planetary_aspects(positions)
            
            if aspects:
                # Create detailed aspects table
                aspect_details = []
                for aspect in aspects:
                    aspect_details.append({
                        'Planet 1': aspect['planet1'],
                        'Planet 2': aspect['planet2'],
                        'Aspect': aspect['aspect'],
                        'Angle': f"{aspect['angle']:.1f}°",
                        'Strength': aspect['strength'],
                        'Orb': f"{aspect['orb_used']:.1f}°",
                        'Type': 'Bullish' if aspect['strength'] > 0.7 else 'Bearish' if aspect['strength'] < 0.3 else 'Neutral'
                    })
                
                aspect_df = pd.DataFrame(aspect_details)
                aspect_df = aspect_df.sort_values('Strength', ascending=False)
                
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
            
            # Display detailed symbol analysis
            st.subheader("Detailed Symbol Analysis")
            
            # Use the selected symbol from sidebar
            if selected_symbol == "All":
                analysis_symbol = "Nifty"  # Default to Nifty
            else:
                analysis_symbol = selected_symbol
            
            # Generate detailed report for the selected symbol
            detailed_report = []
            
            for start_time_str, end_time_str in time_slots:
                start_hour, start_minute = map(int, start_time_str.split(':'))
                start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                
                # Calculate planetary positions and aspects
                positions = calculate_planetary_positions(start_time)
                aspects = calculate_planetary_aspects(positions)
                
                # Generate signals
                signal_data = generate_special_symbol_signals(aspects, analysis_symbol, start_time)
                
                detailed_report.append({
                    'Time Slot': f"{start_time_str} - {end_time_str}",
                    'Signal': signal_data['signal'],
                    'Bullish Strength': signal_data['bullish_strength'],
                    'Bearish Strength': signal_data['bearish_strength'],
                    'Strongest Aspect': signal_data['strongest_aspect'],
                    'All Aspects': signal_data['all_aspects']
                })
            
            # Display detailed report
            for slot in detailed_report:
                st.markdown(f"### {slot['Time Slot']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    signal_class = "signal-bullish" if slot['Signal'] == "Bullish" else "signal-bearish"
                    st.markdown(f"**Signal:** <span class='{signal_class}'>{slot['Signal']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Bullish Strength:** {slot['Bullish Strength']}")
                    st.markdown(f"**Bearish Strength:** {slot['Bearish Strength']}")
                    st.markdown(f"**Strongest Aspect:** {slot['Strongest Aspect']}")
                
                with col2:
                    st.markdown("### Signal Strength")
                    st.progress(slot['Bullish Strength'] / max(slot['Bullish Strength'] + slot['Bearish Strength'], 0.001))
                    st.markdown(f"<span style='color: green'>Bullish: {slot['Bullish Strength']:.2f}</span>", unsafe_allow_html=True)
                    st.progress(slot['Bearish Strength'] / max(slot['Bullish Strength'] + slot['Bearish Strength'], 0.001))
                    st.markdown(f"<span style='color: red'>Bearish: {slot['Bearish Strength']:.2f}</span>", unsafe_allow_html=True)
                
                # Display all transit details
                st.markdown("### All Active Transits")
                if slot['All Aspects']:
                    for aspect in slot['All Aspects']:
                        aspect_class = "aspect-bullish" if slot['Signal'] == "Bullish" else "aspect-bearish"
                        st.markdown(f"""
                        <div class="{aspect_class}">
                            🔮 {aspect['planets']} {aspect['aspect']} (Strength: {aspect['strength']:.2f}) at {aspect['time']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No significant transits affecting this symbol at this time")
                
                st.markdown("---")
    else:
        # Show instructions when no report is generated
        st.info("👆 Please select a date and click 'Generate Daily Report' to view the astrological analysis")

if __name__ == "__main__":
    main()
