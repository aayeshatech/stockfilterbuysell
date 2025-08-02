import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import math
import requests
from typing import Dict, Optional

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

try:
    from skyfield.api import load
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

class PlanetaryDataFetcher:
    """Class to fetch planetary data with multiple fallback methods"""
    
    def __init__(self):
        self.methods = []
        self.setup_available_methods()
    
    def setup_available_methods(self):
        """Setup available data fetching methods"""
        if SWISSEPH_AVAILABLE:
            self.methods.append(('Swiss Ephemeris', self.fetch_swisseph))
        
        if EHEM_AVAILABLE:
            self.methods.append(('Ephem', self.fetch_ephem))
        
        if SKYFIELD_AVAILABLE:
            self.methods.append(('Skyfield', self.fetch_skyfield))
        
        # Always add API methods
        self.methods.append(('Astro.com API', self.fetch_astro_api))
        self.methods.append(('AstDienst', self.fetch_astdienst))
    
    def fetch_planetary_data(self, date_time: datetime) -> Dict[str, float]:
        """Fetch planetary data with fallback methods"""
        errors = []
        
        for method_name, method_func in self.methods:
            try:
                st.info(f"Trying {method_name}...")
                positions = method_func(date_time)
                if positions:
                    st.success(f"Successfully fetched data using {method_name}")
                    return positions
            except Exception as e:
                error_msg = f"{method_name} failed: {str(e)}"
                errors.append(error_msg)
                st.warning(error_msg)
        
        # If all methods failed
        st.error("All data fetching methods failed:")
        for error in errors:
            st.error(f"  - {error}")
        
        return {}
    
    def fetch_swisseph(self, date_time: datetime) -> Dict[str, float]:
        """Fetch using Swiss Ephemeris"""
        if not st.session_state.get('swisseph_initialized', False):
            init_swisseph()
        
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
            positions[name] = pos[0]
        
        return positions
    
    def fetch_ephem(self, date_time: datetime) -> Dict[str, float]:
        """Fetch using ephem library"""
        observer = ephem.Observer()
        observer.date = date_time
        
        planets = {
            'Sun': ephem.Sun(observer),
            'Moon': ephem.Moon(observer),
            'Mercury': ephem.Mercury(observer),
            'Venus': ephem.Venus(observer),
            'Mars': ephem.Mars(observer),
            'Jupiter': ephem.Jupiter(observer),
            'Saturn': ephem.Saturn(observer)
        }
        
        positions = {}
        for name, planet in planets.items():
            lon = math.degrees(planet.ra)
            positions[name] = lon % 360
        
        # Calculate approximate positions for Rahu and Ketu
        # (simplified calculation)
        moon_pos = positions['Moon']
        rahu_pos = (moon_pos + 180) % 360
        ketu_pos = (moon_pos + 0) % 360  # Opposite to Rahu
        
        positions['Rahu'] = rahu_pos
        positions['Ketu'] = ketu_pos
        
        return positions
    
    def fetch_skyfield(self, date_time: datetime) -> Dict[str, float]:
        """Fetch using skyfield library"""
        try:
            eph = load('de421.bsp')
            earth = eph['earth']
            ts = load.timescale()
            t = ts.utc(date_time)
            
            planets = {
                'Sun': eph['sun'],
                'Moon': eph['moon'],
                'Mercury': eph['mercury'],
                'Venus': eph['venus'],
                'Mars': eph['mars'],
                'Jupiter': eph['jupiter'],
                'Saturn': eph['saturn']
            }
            
            positions = {}
            for name, planet in planets.items():
                astrometric = earth.at(t).observe(planet)
