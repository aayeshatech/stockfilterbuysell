import streamlit as st
from datetime import datetime
import swisseph as swe
import pandas as pd
import os

# Configure Swiss Ephemeris path
swe.set_ephe_path(r"C:\Users\a\Downloads\swisseph-master (1)\swisseph-master\ephe")

# Configure page
st.set_page_config(page_title="Professional Astro Calculator", layout="wide")
st.title("♁ Swiss Ephemeris Transit Calculator")

def calculate_transits(date, lat, lon):
    """Calculate precise planetary positions using Swiss Ephemeris"""
    # Set up observer
    jd = swe.julday(date.year, date.month, date.day, 12.0)  # Noon UTC
    
    # Calculate planet positions
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # North Node
        'Ketu': -swe.MEAN_NODE   # South Node
    }
    
    results = []
    for name, p in planets.items():
        # Get precise position
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        if p == swe.MEAN_NODE or p == -swe.MEAN_NODE:
            flags |= swe.FLG_NOGDEFL
        
        pos, ret = swe.calc_ut(jd, p, flags=flags)
        
        # Convert to zodiac position
        sign_num = int(pos[0] / 30)
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
                "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        sign = signs[sign_num]
        degree = pos[0] % 30
        minutes = (degree - int(degree)) * 60
        
        # House position (Placidus)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        house = swe.house_pos(cusps[0], pos[0], pos[1], lat, lon, b'P') + 1
        
        results.append({
            'Planet': name,
            'Position': f"{int(degree)}°{int(minutes)}' {sign}",
            'Speed': f"{pos[3]:.2f}°/day",
            'Retrograde': "◀" if pos[3] < 0 else "▶",
            'House': f"{int(house)}H",
            'Constellation': get_nakshatra(pos[0])
        })
    
    return pd.DataFrame(results)

def get_nakshatra(longitude):
    """Calculate Vedic nakshatra (27 lunar mansions)"""
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", 
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", 
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", 
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", 
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Purva Bhadra", "Uttara Bhadra", "Revati"
    ]
    index = int((longitude * 27) / 360)
    return nakshatras[index]

# User Interface
with st.sidebar:
    st.header("Configuration")
    selected_date = st.date_input("Date", datetime.today())
    lat = st.number_input("Latitude", value=40.7128)  # New York City
    lon = st.number_input("Longitude", value=-74.0060)
    
    if st.button("Calculate Exact Positions"):
        with st.spinner("Computing planetary data..."):
            try:
                transits = calculate_transits(selected_date, lat, lon)
                
                # Display results
                st.subheader(f"Planetary Positions for {selected_date.strftime('%B %d, %Y')}")
                
                # Color formatting
                def style_row(row):
                    color = 'red' if row['Retrograde'] == '◀' else 'green'
                    return [f'color: {color}' for _ in row]
                
                st.dataframe(
                    transits.style.apply(style_row, axis=1),
                    column_config={
                        "Position": st.column_config.TextColumn(width="large"),
                        "Speed": "Daily Speed"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Additional info
                st.info("◀ = Retrograde | ▶ = Direct Motion")
                
            except Exception as e:
                st.error(f"Calculation error: {str(e)}")

# Instructions
with st.expander("Installation Guide"):
    st.markdown("""
    1. Install Swiss Ephemeris:
       ```bash
       pip install pyswisseph
       ```
    2. Download ephemeris files from [Astrodienst](https://www.astro.com/ftp/swisseph/ephe/)
    3. Set the path in code:
       ```python
       swe.set_ephe_path("/path/to/ephe/folder")
       ```
    """)
 
st.caption(f"Using Swiss Ephemeris {swe.version()} | Data files: {swe.get_ephe_path()}")
