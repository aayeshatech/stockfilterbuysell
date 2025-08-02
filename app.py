import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import math
from typing import Dict, Optional, List
import pytz
import requests
from bs4 import BeautifulSoup
import re

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
    .planetary-position-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
    .planetary-position-table th, .planetary-position-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .planetary-position-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .planetary-position-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .data-source {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
        margin-top: 0.5rem;
    }
    .error-message {
        color: #d62728;
        font-weight: bold;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 0.5rem;
        border-left: 4px solid #d62728;
    }
    .info-message {
        color: #0c5460;
        font-weight: bold;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 0.5rem;
        border-left: 4px solid #0c5460;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    .website-access-info {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .website-access-info h3 {
        margin-top: 0;
        color: #856404;
    }
    .website-access-info p {
        margin-bottom: 0.5rem;
    }
    .website-access-info code {
        background-color: #f8f9fa;
        padding: 0.2rem 0.4rem;
        border-radius: 0.2rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Function to fetch planetary data from the website with enhanced error handling
def fetch_planetary_data_from_website(date):
    """
    Fetch planetary data from astronomics.ai for a given date
    Returns a dictionary with planetary positions and aspects
    """
    try:
        # Format the date for the URL
        date_str = date.strftime("%Y-%m-%d")
        url = f"https://data.astronomics.ai/almanac/{date_str}"
        
        # Send a request to the website with enhanced headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract planetary positions
            planetary_data = {}
            
            # Look for tables containing planetary data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains planetary data
                headers = [th.text.strip() for th in table.find_all('th')]
                
                if 'Planet' in headers and 'Zodiac' in headers:
                    # Extract rows
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            planet = cells[0].text.strip()
                            zodiac = cells[1].text.strip()
                            
                            # Extract additional data if available
                            motion = cells[2].text.strip() if len(cells) > 2 else ""
                            nakshatra = cells[3].text.strip() if len(cells) > 3 else ""
                            pada = cells[4].text.strip() if len(cells) > 4 else ""
                            pos_in_zodiac = cells[5].text.strip() if len(cells) > 5 else ""
                            declination = cells[6].text.strip() if len(cells) > 6 else ""
                            
                            # Extract sign lord, star lord, sub lord if available
                            sign_lord = cells[7].text.strip() if len(cells) > 7 else ""
                            star_lord = cells[8].text.strip() if len(cells) > 8 else ""
                            sub_lord = cells[9].text.strip() if len(cells) > 9 else ""
                            
                            # Store the data
                            planetary_data[planet] = {
                                'zodiac': zodiac,
                                'motion': motion,
                                'nakshatra': nakshatra,
                                'pada': pada,
                                'pos_in_zodiac': pos_in_zodiac,
                                'declination': declination,
                                'sign_lord': sign_lord,
                                'star_lord': star_lord,
                                'sub_lord': sub_lord
                            }
            
            # Extract planetary aspects if available
            aspects = []
            aspect_tables = soup.find_all('table', class_='aspect-table')
            
            for table in aspect_tables:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        planet1 = cells[0].text.strip()
                        planet2 = cells[1].text.strip()
                        aspect_type = cells[2].text.strip()
                        strength = float(cells[3].text.strip()) if len(cells) > 3 and cells[3].text.strip() else 0.5
                        angle = float(cells[4].text.strip()) if len(cells) > 4 and cells[4].text.strip() else 0.0
                        orb = float(cells[5].text.strip()) if len(cells) > 5 and cells[5].text.strip() else 0.0
                        
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_type,
                            'strength': strength,
                            'angle': angle,
                            'orb_used': orb
                        })
            
            return {
                'planetary_positions': planetary_data,
                'aspects': aspects,
                'source': 'astronomics.ai'
            }
        else:
            return {
                'error': f"HTTP Error {response.status_code}: Failed to fetch data from astronomics.ai",
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'error': f"Request Exception: {str(e)}",
            'status_code': None
        }
    except Exception as e:
        return {
            'error': f"Error: {str(e)}",
            'status_code': None
        }

# Function to fetch intraday planetary data for specific times
def fetch_intraday_planetary_data(date, time_slots):
    """
    Fetch intraday planetary data for specific time slots on a given date
    Returns a dictionary with time slots as keys and planetary data as values
    """
    intraday_data = {}
    
    for start_time_str, end_time_str in time_slots:
        # Parse time strings
        start_hour, start_minute = map(int, start_time_str.split(':'))
        
        # Create datetime objects for the time slot
        start_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
        
        # Format the datetime for the URL
        datetime_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        url = f"https://data.astronomics.ai/almanac/{datetime_str}"
        
        try:
            # Send a request to the website with enhanced headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract planetary positions
                planetary_data = {}
                
                # Look for tables containing planetary data
                tables = soup.find_all('table')
                
                for table in tables:
                    # Check if this table contains planetary data
                    headers = [th.text.strip() for th in table.find_all('th')]
                    
                    if 'Planet' in headers and 'Zodiac' in headers:
                        # Extract rows
                        rows = table.find_all('tr')[1:]  # Skip header row
                        
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 2:
                                planet = cells[0].text.strip()
                                zodiac = cells[1].text.strip()
                                
                                # Extract additional data if available
                                motion = cells[2].text.strip() if len(cells) > 2 else ""
                                nakshatra = cells[3].text.strip() if len(cells) > 3 else ""
                                pada = cells[4].text.strip() if len(cells) > 4 else ""
                                pos_in_zodiac = cells[5].text.strip() if len(cells) > 5 else ""
                                declination = cells[6].text.strip() if len(cells) > 6 else ""
                                
                                # Extract sign lord, star lord, sub lord if available
                                sign_lord = cells[7].text.strip() if len(cells) > 7 else ""
                                star_lord = cells[8].text.strip() if len(cells) > 8 else ""
                                sub_lord = cells[9].text.strip() if len(cells) > 9 else ""
                                
                                # Store the data
                                planetary_data[planet] = {
                                    'zodiac': zodiac,
                                    'motion': motion,
                                    'nakshatra': nakshatra,
                                    'pada': pada,
                                    'pos_in_zodiac': pos_in_zodiac,
                                    'declination': declination,
                                    'sign_lord': sign_lord,
                                    'star_lord': star_lord,
                                    'sub_lord': sub_lord
                                }
                
                # Extract planetary aspects if available
                aspects = []
                aspect_tables = soup.find_all('table', class_='aspect-table')
                
                for table in aspect_tables:
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            planet1 = cells[0].text.strip()
                            planet2 = cells[1].text.strip()
                            aspect_type = cells[2].text.strip()
                            strength = float(cells[3].text.strip()) if len(cells) > 3 and cells[3].text.strip() else 0.5
                            angle = float(cells[4].text.strip()) if len(cells) > 4 and cells[4].text.strip() else 0.0
                            orb = float(cells[5].text.strip()) if len(cells) > 5 and cells[5].text.strip() else 0.0
                            
                            aspects.append({
                                'planet1': planet1,
                                'planet2': planet2,
                                'aspect': aspect_type,
                                'strength': strength,
                                'angle': angle,
                                'orb_used': orb
                            })
                
                intraday_data[start_time_str] = {
                    'planetary_positions': planetary_data,
                    'aspects': aspects,
                    'source': 'astronomics.ai'
                }
            else:
                intraday_data[start_time_str] = {
                    'error': f"HTTP Error {response.status_code}: Failed to fetch data for {start_time_str}",
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            intraday_data[start_time_str] = {
                'error': f"Request Exception for {start_time_str}: {str(e)}",
                'status_code': None
            }
        except Exception as e:
            intraday_data[start_time_str] = {
                'error': f"Error for {start_time_str}: {str(e)}",
                'status_code': None
            }
    
    return intraday_data

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
def generate_special_transit_report(selected_date, watchlist, sectors, selected_time_slot=None, intraday_data=None):
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
        # Get data for this time slot
        if intraday_data and start_time_str in intraday_data:
            time_slot_data = intraday_data[start_time_str]
            if 'error' not in time_slot_data:
                positions = time_slot_data['planetary_positions']
                aspects = time_slot_data['aspects']
                source = time_slot_data.get('source', 'astronomics.ai')
            else:
                # Skip this time slot if data is not available
                continue
        else:
            # Skip this time slot if data is not available
            continue
        
        # Generate signals for each special symbol
        for symbol in special_symbols:
            sector = sectors.get(symbol, 'Unknown')
            
            # Parse the time string to create a datetime object
            start_hour, start_minute = map(int, start_time_str.split(':'))
            current_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
            
            signal_data = generate_special_symbol_signals(aspects, symbol, current_time)
            
            # Add to report data
            report_data.append({
                'Time Factor': f"{start_time_str} - {end_time_str}",
                'Index Name': symbol,
                'Bullish/Bearish': signal_data['signal'],
                'Time': start_time_str,
                'Planetary Aspect': signal_data['strongest_aspect'],
                'Bullish Strength': signal_data['bullish_strength'],
                'Bearish Strength': signal_data['bearish_strength'],
                'All Aspects': signal_data['all_aspects'],
                'Planetary Positions': positions,
                'Data Source': source
            })
    
    return report_data

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
    
    # Display information about website access
    st.markdown("""
    <div class="website-access-info">
        <h3>📡 Data Source Information</h3>
        <p>This dashboard fetches planetary data from <a href="https://data.astronomics.ai/almanac/" target="_blank">data.astronomics.ai/almanac/</a>.</p>
        <p>If you're experiencing issues accessing the data, it might be due to:</p>
        <ul>
            <li>Website restrictions or rate limiting</li>
            <li>Geographical access limitations</li>
            <li>Temporary website maintenance</li>
        </ul>
        <p>The URL format used is: <code>https://data.astronomics.ai/almanac/YYYY-MM-DD</code> for daily data and <code>https://data.astronomics.ai/almanac/YYYY-MM-DDTHH:MM:SS</code> for intraday data.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        
        # Fetch intraday planetary data
        with st.spinner("Fetching intraday planetary data from astronomics.ai..."):
            intraday_data = fetch_intraday_planetary_data(selected_date, time_slots)
        
        # Check if we have any successful data
        successful_data = {k: v for k, v in intraday_data.items() if 'error' not in v}
        
        if not successful_data:
            st.error("Failed to fetch data from astronomics.ai for any time slot. Please check the website accessibility and try again later.")
            
            # Display detailed error information
            st.markdown('<div class="error-message">Error Details:</div>', unsafe_allow_html=True)
            
            for time_slot, data in intraday_data.items():
                if 'error' in data:
                    st.markdown(f"""
                    <div class="error-message">
                        <strong>Time Slot:</strong> {time_slot}<br>
                        <strong>Error:</strong> {data['error']}<br>
                        <strong>Status Code:</strong> {data['status_code'] if data['status_code'] else 'N/A'}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Provide troubleshooting suggestions
            st.markdown("""
            <div class="info-message">
                <strong>Troubleshooting Suggestions:</strong><br>
                1. Check if the website is accessible by visiting: <a href="https://data.astronomics.ai/almanac/" target="_blank">https://data.astronomics.ai/almanac/</a><br>
                2. Try again later as the website might be temporarily unavailable<br>
                3. Contact the website administrator if the issue persists<br>
                4. Check if there are any geographical restrictions accessing the website
            </div>
            """, unsafe_allow_html=True)
            
            # Don't generate the report if we don't have data
            st.session_state.report_generated = False
            st.rerun()
        
        # Generate special transit report
        with st.spinner("Generating special transit report..."):
            special_report_data = generate_special_transit_report(selected_date, watchlist, sectors, selected_time_slot, intraday_data)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Special Transit Report", "Planetary Positions", "Detailed Analysis"])
        
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
                
                # Show data source
                if special_report_data:
                    source = special_report_data[0].get('Data Source', 'astronomics.ai')
                    st.markdown(f'<div class="data-source">Data source: {source}</div>', unsafe_allow_html=True)
                
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
            st.header("Detailed Planetary Positions")
            
            # Get the first time slot for planetary positions
            time_slot = selected_time_slot if selected_time_slot else time_slots[0]
            start_time_str, end_time_str = time_slot
            
            # Get data for this time slot
            if intraday_data and start_time_str in intraday_data:
                time_slot_data = intraday_data[start_time_str]
                if 'error' not in time_slot_data:
                    positions = time_slot_data['planetary_positions']
                    source = time_slot_data.get('source', 'astronomics.ai')
                else:
                    st.info("Planetary positions not available for this time slot")
                    positions = {}
                    source = "N/A"
            else:
                st.info("Planetary positions not available for this time slot")
                positions = {}
                source = "N/A"
            
            if positions:
                # Create detailed positions table
                pos_data = []
                for planet, data in positions.items():
                    pos_data.append({
                        'Planet': planet,
                        'Date': selected_date.strftime("%Y-%m-%d"),
                        'Time': start_time_str,
                        'Motion': data.get('motion', ''),
                        'Sign Lord': data.get('sign_lord', ''),
                        'Star Lord': data.get('star_lord', ''),
                        'Sub Lord': data.get('sub_lord', ''),
                        'Zodiac': data.get('zodiac', ''),
                        'Nakshatra': data.get('nakshatra', ''),
                        'Pada': data.get('pada', ''),
                        'Pos in Zodiac': data.get('pos_in_zodiac', ''),
                        'Declination': data.get('declination', '')
                    })
                
                pos_df = pd.DataFrame(pos_data)
                
                # Display table with custom styling
                st.markdown("""
                <table class="planetary-position-table">
                    <thead>
                        <tr>
                            <th>Planet</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Motion</th>
                            <th>Sign Lord</th>
                            <th>Star Lord</th>
                            <th>Sub Lord</th>
                            <th>Zodiac</th>
                            <th>Nakshatra</th>
                            <th>Pada</th>
                            <th>Pos in Zodiac</th>
                            <th>Declination</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in pos_df.iterrows():
                    st.markdown(f"""
                    <tr>
                        <td>{row['Planet']}</td>
                        <td>{row['Date']}</td>
                        <td>{row['Time']}</td>
                        <td>{row['Motion']}</td>
                        <td>{row['Sign Lord']}</td>
                        <td>{row['Star Lord']}</td>
                        <td>{row['Sub Lord']}</td>
                        <td>{row['Zodiac']}</td>
                        <td>{row['Nakshatra']}</td>
                        <td>{row['Pada']}</td>
                        <td>{row['Pos in Zodiac']}</td>
                        <td>{row['Declination']}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                    </tbody>
                </table>
                """, unsafe_allow_html=True)
                
                # Show data source
                st.markdown(f'<div class="data-source">Data source: {source}</div>', unsafe_allow_html=True)
            else:
                st.info("Planetary positions not available")
        
        with tab3:
            st.header("Detailed Astrological Analysis")
            
            # Display planetary aspects
            st.subheader("Planetary Aspects")
            
            # Get the first time slot for planetary aspects
            time_slot = selected_time_slot if selected_time_slot else time_slots[0]
            start_time_str, end_time_str = time_slot
            
            # Get data for this time slot
            if intraday_data and start_time_str in intraday_data:
                time_slot_data = intraday_data[start_time_str]
                if 'error' not in time_slot_data:
                    aspects = time_slot_data['aspects']
                    source = time_slot_data.get('source', 'astronomics.ai')
                else:
                    st.info("Planetary aspects not available for this time slot")
                    aspects = []
                    source = "N/A"
            else:
                st.info("Planetary aspects not available for this time slot")
                aspects = []
                source = "N/A"
            
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
                
                # Show data source
                st.markdown(f'<div class="data-source">Data source: {source}</div>', unsafe_allow_html=True)
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
                # Get data for this time slot
                if intraday_data and start_time_str in intraday_data:
                    time_slot_data = intraday_data[start_time_str]
                    if 'error' not in time_slot_data:
                        positions = time_slot_data['planetary_positions']
                        aspects = time_slot_data['aspects']
                    else:
                        continue
                else:
                    continue
                
                # Parse the time string to create a datetime object
                start_hour, start_minute = map(int, start_time_str.split(':'))
                current_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                
                # Generate signals
                signal_data = generate_special_symbol_signals(aspects, analysis_symbol, current_time)
                
                detailed_report.append({
                    'Time Slot': f"{start_time_str} - {end_time_str}",
                    'Signal': signal_data['signal'],
                    'Bullish Strength': signal_data['bullish_strength'],
                    'Bearish Strength': signal_data['bearish_strength'],
                    'Strongest Aspect': signal_data['strongest_aspect'],
                    'All Aspects': signal_data['all_aspects'],
                    'Planetary Positions': positions
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
