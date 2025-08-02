import streamlit as st
from datetime import datetime
import pandas as pd
import os
import urllib.request
import zipfile
import shutil
import tempfile

# Create ephemeris directory if it doesn't exist
EPHE_DIR = os.path.join(os.path.dirname(__file__), 'ephe')

def ensure_directory_exists(directory):
    """Ensure a directory exists, handling potential errors"""
    try:
        # Check if path exists
        if os.path.exists(directory):
            # If it exists but is not a directory, remove it
            if not os.path.isdir(directory):
                st.warning(f"Path {directory} exists but is not a directory. Removing it...")
                os.remove(directory)
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            st.success(f"Created directory: {directory}")
        
        # Verify it's actually a directory
        if not os.path.isdir(directory):
            st.error(f"Failed to create directory: {directory}")
            return False
        return True
    except Exception as e:
        st.error(f"Failed to create directory {directory}: {str(e)}")
        return False

# Ensure the ephemeris directory exists
if not ensure_directory_exists(EPHE_DIR):
    st.error("Cannot proceed without ephemeris directory. Please check permissions.")
    st.stop()

def check_required_files():
    """Check if required ephemeris files exist"""
    required_files = ['sepl_18.se1', 'semo_18.se1', 'seas_18.se1']
    missing_files = []
    
    for filename in required_files:
        filepath = os.path.join(EPHE_DIR, filename)
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:  # Check if file exists and is not empty
            missing_files.append(filename)
    
    return missing_files

def download_ephemeris_files():
    """Download required ephemeris files using multiple methods"""
    missing_files = check_required_files()
    if not missing_files:
        return True
    
    st.warning(f"Missing ephemeris files: {', '.join(missing_files)}")
    
    # Try multiple download sources
    download_sources = [
        # Primary source - GitHub raw files
        {
            'sepl_18.se1': 'https://github.com/aloistr/swisseph/raw/master/ephe/sepl_18.se1',
            'semo_18.se1': 'https://github.com/aloistr/swisseph/raw/master/ephe/semo_18.se1',
            'seas_18.se1': 'https://github.com/aloistr/swisseph/raw/master/ephe/seas_18.se1'
        },
        # Alternative source - Swiss Ephemeris official
        {
            'sepl_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1',
            'semo_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/semo_18.se1',
            'seas_18.se1': 'https://www.astro.com/ftp/swisseph/ephe/seas_18.se1'
        },
        # Alternative source - Mirror
        {
            'sepl_18.se1': 'https://raw.githubusercontent.com/mnabeelp/PySwissEphemeris/master/ephe/sepl_18.se1',
            'semo_18.se1': 'https://raw.githubusercontent.com/mnabeelp/PySwissEphemeris/master/ephe/semo_18.se1',
            'seas_18.se1': 'https://raw.githubusercontent.com/mnabeelp/PySwissEphemeris/master/ephe/seas_18.se1'
        }
    ]
    
    # Try each source
    for source_num, source in enumerate(download_sources):
        st.write(f"Trying download source {source_num + 1}...")
        success = True
        
        for filename in missing_files:
            if filename in source:
                url = source[filename]
                filepath = os.path.join(EPHE_DIR, filename)
                
                try:
                    st.write(f"Downloading {filename}...")
                    urllib.request.urlretrieve(url, filepath)
                    
                    # Verify file was downloaded correctly
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                        st.success(f"✓ {filename} downloaded successfully")
                    else:
                        st.error(f"Downloaded file {filename} is invalid")
                        success = False
                        
                except Exception as e:
                    st.error(f"Failed to download {filename}: {str(e)}")
                    success = False
        
        if success:
            st.success("All ephemeris files downloaded successfully!")
            return True
    
    # If all sources failed, try the zip method
    st.warning("Direct downloads failed. Trying with zip archive...")
    
    zip_sources = [
        "https://www.astro.com/swisseph/download/sweph_1800_2400.zip",
        "https://github.com/aloistr/swisseph/archive/refs/heads/master.zip"
    ]
    
    for zip_url in zip_sources:
        try:
            st.write(f"Downloading from {zip_url}...")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "sweph.zip")
                urllib.request.urlretrieve(zip_url, zip_path)
                
                st.write("Extracting files...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Look for ephemeris files in the extracted content
                extracted_ephe_dir = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'ephe' in dirs:
                        extracted_ephe_dir = os.path.join(root, 'ephe')
                        break
                
                if extracted_ephe_dir:
                    # Copy missing files
                    for filename in missing_files:
                        src_path = os.path.join(extracted_ephe_dir, filename)
                        if os.path.exists(src_path):
                            dst_path = os.path.join(EPHE_DIR, filename)
                            shutil.copy2(src_path, dst_path)
                            st.success(f"✓ {filename} extracted successfully")
                        else:
                            st.error(f"File {filename} not found in archive")
                    
                    # Check if all files were extracted
                    if not check_required_files():
                        st.success("All ephemeris files extracted successfully!")
                        return True
                else:
                    st.error("Could not find ephemeris files in the downloaded archive.")
                    
        except Exception as e:
            st.error(f"Failed to download or extract {zip_url}: {str(e)}")
    
    return False

def manual_upload_files():
    """Allow user to manually upload ephemeris files"""
    st.write("### Manual Upload")
    st.write("Please upload the required ephemeris files:")
    
    required_files = ['sepl_18.se1', 'semo_18.se1', 'seas_18.se1']
    uploaded_files = {}
    
    for filename in required_files:
        uploaded_file = st.file_uploader(f"Upload {filename}", type=["se1"], key=filename)
        if uploaded_file is not None:
            uploaded_files[filename] = uploaded_file
    
    if uploaded_files and st.button("Save Uploaded Files"):
        success_count = 0
        for filename, file in uploaded_files.items():
            try:
                # Ensure the directory exists and is writable
                if not os.path.isdir(EPHE_DIR):
                    st.error(f"EPHE_DIR is not a directory: {EPHE_DIR}")
                    continue
                
                # Create the file path
                file_path = os.path.join(EPHE_DIR, filename)
                
                # Write the file
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Verify the file was written correctly
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    st.success(f"✓ {filename} saved successfully")
                    success_count += 1
                else:
                    st.error(f"Failed to save {filename}")
                    
            except Exception as e:
                st.error(f"Error saving {filename}: {str(e)}")
        
        # Check if all files were saved
        if success_count == len(required_files):
            st.success("All required files have been uploaded and saved!")
            return True
        else:
            st.error(f"Only {success_count} out of {len(required_files)} files were saved successfully")
            return False
    
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
    
    # Try automatic download
    if download_ephemeris_files():
        swe = initialize_swisseph()
        if swe is None:
            st.error("Still failed after downloading files. Please check the logs.")
        else:
            st.success("Swiss Ephemeris initialized successfully!")
    
    # If automatic download failed, try manual upload
    if swe is None:
        st.error("Automatic download failed. Please try manual upload.")
        if manual_upload_files():
            swe = initialize_swisseph()
            if swe is None:
                st.error("Still failed after uploading files. Please check the logs.")
            else:
                st.success("Swiss Ephemeris initialized successfully!")
    
    # If all methods failed, stop the app
    if swe is None:
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
    2. The app will attempt to automatically download required ephemeris files
    3. If automatic download fails, use the manual upload option
    
    ### Manual Download Links:
    If you need to download the files manually:
    - [sepl_18.se1](https://github.com/aloistr/swisseph/raw/master/ephe/sepl_18.se1)
    - [semo_18.se1](https://github.com/aloistr/swisseph/raw/master/ephe/semo_18.se1)
    - [seas_18.se1](https://github.com/aloistr/swisseph/raw/master/ephe/seas_18.se1)
    """)
 
st.caption(f"Using Swiss Ephemeris {swe.version()} | Data files: {swe.get_ephe_path()}")
