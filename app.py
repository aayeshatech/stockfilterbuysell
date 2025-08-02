import pandas as pd
from datetime import datetime, timedelta

# Sample planetary data (from your image)
current_transits = {
    "retrograde": [{"planet": "Mercury", "sign": "Sagittarius", "nakshatra": "Purva Ashadha", "pada": 3}],
    "direct": [
        {"planet": "Sun", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "pada": 4},
        {"planet": "Moon", "sign": "Gemini", "nakshatra": "Ardra", "pada": 1},
        {"planet": "Mars", "sign": "Gemini", "nakshatra": "Punarvasu", "pada": 1},
        {"planet": "Jupiter", "sign": "Pisces", "nakshatra": "Revati", "pada": 4},
        {"planet": "Venus", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "pada": 4},
        {"planet": "Saturn", "sign": "Aquarius", "nakshatra": "Purva Bhadrapada", "pada": 2}
    ]
}

# Sector mappings based on Vedic astrology
planet_sectors = {
    "Sun": ["Infrastructure", "Energy", "Government"],
    "Moon": ["Liquids", "Shipping", "Retail"],
    "Mars": ["Metals", "Defense", "Technology"],
    "Mercury": ["Communication", "IT", "Logistics"],
    "Jupiter": ["Pharma", "Banking", "Education"],
    "Venus": ["Luxury", "Automobiles", "Entertainment"],
    "Saturn": ["Utilities", "Real Estate", "Heavy Industries"]
}

# Sample stock universe
stocks_database = [
    {"symbol": "TATASTEEL", "sector": "Metals", "nakshatra": "Rohini"},
    {"symbol": "RELIANCE", "sector": "Energy", "nakshatra": "Uttara Ashadha"},
    {"symbol": "INFY", "sector": "IT", "nakshatra": "Hasta"},
    {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
    {"symbol": "TATAPOWER", "sector": "Utilities", "nakshatra": "Purva Bhadrapada"}
]

def generate_watchlist(transits):
    watchlist = []
    
    # Check retrograde first (generally avoid)
    for planet in transits["retrograde"]:
        if planet["planet"] == "Mercury":
            print(f"⚠️ Mercury Retrograde Alert: Avoid new investments until {datetime.now() + timedelta(days=14)}")
    
    # Analyze direct planets
    favorable_sectors = set()
    for planet in transits["direct"]:
        favorable_sectors.update(planet_sectors.get(planet["planet"], []))
        
        # Special logic for Jupiter in Revati (strong buy signal)
        if planet["planet"] == "Jupiter" and planet["nakshatra"] == "Revati":
            favorable_sectors.add("Pharma")
            favorable_sectors.add("Shipping")
    
    # Find matching stocks
    for stock in stocks_database:
        if stock["sector"] in favorable_sectors:
            signal = "BUY"  # Basic logic - refine with more rules
            strength = "Strong" if any(
                p["nakshatra"] == stock["nakshatra"] 
                for p in transits["direct"]
            ) else "Moderate"
            
            watchlist.append({
                "Stock": stock["symbol"],
                "Sector": stock["sector"],
                "Signal": signal,
                "Strength": strength,
                "Planetary Influence": [
                    p["planet"] for p in transits["direct"] 
                    if stock["sector"] in planet_sectors.get(p["planet"], [])
                ]
            })
    
    return pd.DataFrame(watchlist)

# Generate and display watchlist
watchlist_df = generate_watchlist(current_transits)
print("\n🌟 Astro Stock Watchlist (Next 7 Days)\n")
print(watchlist_df.to_string(index=False))

# Add trading calendar (simplified)
print("\n📅 Favorable Trading Times:")
print(f"{datetime.now().strftime('%b %d')}: Moon trine Jupiter (Good for buying)")
print(f"{(datetime.now() + timedelta(days=3)).strftime('%b %d')}: Venus enters Capricorn (Stable investments)")
print(f"{(datetime.now() + timedelta(days=6)).strftime('%b %d')}: Mercury square Mars (Avoid trading)")
