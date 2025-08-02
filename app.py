import streamlit as st
from datetime import datetime
import pandas as pd
import os
import urllib.request
import zipfile
import shutil

# Create ephemeris directory if it doesn't exist
EPHE_DIR = os.path.join(os.path.dirname(__file__), 'ephe')
os.makedirs(EPHE_DIR, exist_ok=True)

def download_ephemeris_files():
    """Download required ephemeris files using the zip archive"""
    try:
        # URL for the complete ephemeris files zip
        zip_url = "https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1"
        
        # We'll try individual files first, then fall back to zip if needed
        files_to_download = {
            'sepl_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1',
            'semo_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/semo_18.se1',
            'seas_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/seas_18.se1'
        }
        
        st.warning("Downloading ephemeris files...")
        progress_bar = st.progress(0)
        
        # Try downloading individual files
        success = True
        for i, (filename, url) in enumerate(files_to_download.items()):
            filepath = os.path.join(EPHE_DIR, filename)
            
            if not os.path.exists(filepath):
                try:
                    st.write(f"Downloading {filename}...")
                    urllib.request.urlretrieve(url, filepath)
                    st.success(f"✓ {filename} downloaded successfully")
                except Exception as e:
                    st.error(f"Failed to download {filename}: {str(e)}")
                    success = False
            
            progress_bar.progress((i + 1) / len(files_to_download))
        
        if success:
            progress_bar.progress(100)
            st.success("All ephemeris files downloaded successfully!")
            return True
        
        # If individual downloads failed, try the zip method
        st.warning("Individual downloads failed. Trying alternative method...")
        zip_path = os.path.join(EPHE_DIR, "sweph.zip")
        zip_url = "https://www.astro.com/swisseph/download/sweph_1800_2400.zip"
        
        st.write("Downloading complete ephemeris archive...")
        urllib.request.urlretrieve(zip_url, zip_path)
        
        st.write("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(EPHE_DIR)
        
        # Clean up zip file
        os.remove(zip_path)
        
        # Move files to the correct location if needed
        extracted_dir = os.path.join(EPHE_DIR, "ephe")
        if os.path.exists(extracted_dir):
            for file in os.listdir(extracted_dir):
                shutil.move(os.path.join(extracted_dir, file), EPHE_DIR)
            os.rmdir(extracted_dir)
        
        progress_bar.progress(100)
        st.success("Ephemeris files downloaded and extracted successfully!")
        return True
        
    except Exception as e:
        st.error(f"Failed to download ephemeris files: {str(e)}")
        return False

# Initialize Swiss Ephemeris
def initialize_swisseph():
    """Initialize Swiss Ephemeris with proper error handling"""
    try:
        import swisseph as swe
        # Set ephemeris path as bytes to avoid 'str' object not callable error
        swe.set_ephe_path(EPHE_DIR.encode('utf-8'))
        # Test with a simple calculation
        swe.julday(2023, 1, 1)
        return swe
    except Exception as e:
        st.error(f"Swiss Ephemeris initialization failed: {str(e)}")
        return None

# Try to initialize Swiss Ephemeris
swe = initialize_swisseph()
if swe is None:
    st.info("Attempting to download required ephemeris files...")
    if download_ephemeris_files():
        swe = initialize_swisseph()
        if swe is None:
            st.error("Still failed after downloading files. Please check the logs.")
            st.stop()
    else:
        st.error("Failed to initialize Swiss Ephemeris. Please check the logs.")
        st.stop()

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
    ### For Local Installation:
    1. Install required packages:
       ```bash
       pip install streamlit pandas pyswisseph
       ```
    2. Download ephemeris files from [Astrodienst](https://www.astro.com/ftp/swisseph/ephe/)
    3. Create an 'ephe' folder in your project directory
    4. Place the downloaded files in the 'ephe' folder
    
    ### For Streamlit Cloud:
    1. Create a requirements.txt with:
       ```
       streamlit
       pandas
       pyswisseph
       ```
    2. The app will automatically download required ephemeris files
    """)
 
st.caption(f"Using Swiss Ephemeris {swe.version()} | Data files: {swe.get_ephe_path()}")
