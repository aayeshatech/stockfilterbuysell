"""
Astro Stock Watchlist Generator
- No external dependencies except pandas
- Handles retrograde/direct planet analysis
- Includes trading timing suggestions
"""

import pandas as pd
from datetime import datetime, timedelta

class AstroStockAdvisor:
    def __init__(self):
        self.planet_sectors = {
            "Sun": ["Infrastructure", "Energy", "Government"],
            "Moon": ["Liquids", "Shipping", "Retail"],
            "Mars": ["Metals", "Defense", "Technology"],
            "Mercury": ["Communication", "IT", "Logistics"],
            "Jupiter": ["Pharma", "Banking", "Education"],
            "Venus": ["Luxury", "Automobiles", "Entertainment"],
            "Saturn": ["Utilities", "Real Estate", "Heavy Industries"]
        }
        
        self.stocks_database = [
            {"symbol": "TATASTEEL", "sector": "Metals", "nakshatra": "Rohini"},
            {"symbol": "RELIANCE", "sector": "Energy", "nakshatra": "Uttara Ashadha"},
            {"symbol": "INFY", "sector": "IT", "nakshatra": "Hasta"},
            {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
            {"symbol": "TATAPOWER", "sector": "Utilities", "nakshatra": "Purva Bhadrapada"}
        ]
        
        self.current_transits = self.get_current_transits()

    def get_current_transits(self):
        """Mock planetary data - replace with API in production"""
        return {
            "retrograde": [
                {"planet": "Mercury", "sign": "Sagittarius", "nakshatra": "Purva Ashadha", "pada": 3}
            ],
            "direct": [
                {"planet": "Sun", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "pada": 4},
                {"planet": "Moon", "sign": "Gemini", "nakshatra": "Ardra", "pada": 1},
                {"planet": "Jupiter", "sign": "Pisces", "nakshatra": "Revati", "pada": 4},
                {"planet": "Venus", "sign": "Capricorn", "nakshatra": "Uttara Ashadha", "pada": 4}
            ]
        }

    def generate_watchlist(self):
        """Core analysis engine"""
        watchlist = []
        warning = ""
        
        # Retrograde warnings
        for p in self.current_transits["retrograde"]:
            if p["planet"] == "Mercury":
                warning = f"⚠️ Mercury Retrograde ({p['nakshatra']}): Avoid new investments until {(datetime.now() + timedelta(days=14)).strftime('%b %d')}"
        
        # Find favorable sectors
        favorable_sectors = set()
        for planet in self.current_transits["direct"]:
            favorable_sectors.update(self.planet_sectors.get(planet["planet"], []))
            
            # Special boosts
            if planet["planet"] == "Jupiter" and planet["nakshatra"] == "Revati":
                favorable_sectors.add("Pharma")
        
        # Match stocks
        for stock in self.stocks_database:
            if stock["sector"] in favorable_sectors:
                strength = "Strong" if any(
                    p["nakshatra"] == stock["nakshatra"] 
                    for p in self.current_transits["direct"]
                ) else "Moderate"
                
                watchlist.append({
                    "Stock": stock["symbol"],
                    "Sector": stock["sector"],
                    "Signal": "BUY",
                    "Strength": strength,
                    "Planets": ", ".join(
                        p["planet"] for p in self.current_transits["direct"] 
                        if stock["sector"] in self.planet_sectors.get(p["planet"], [])
                    )
                })
        
        return pd.DataFrame(watchlist), warning

    def get_trading_calendar(self):
        """Generate favorable time windows"""
        return [
            {"Date": (datetime.now() + timedelta(days=1)).strftime('%b %d'),
             "Event": "Moon trine Jupiter",
             "Action": "Good for buying"},
            
            {"Date": (datetime.now() + timedelta(days=4)).strftime('%b %d'),
             "Event": "Venus conjunct Sun",
             "Action": "Stable investments"},
            
            {"Date": (datetime.now() + timedelta(days=7)).strftime('%b %d'),
             "Event": "Mars square Saturn",
             "Action": "Avoid trading"}
        ]

if __name__ == "__main__":
    advisor = AstroStockAdvisor()
    
    print("\n" + "="*50)
    print("🌟 ASTROLOGICAL STOCK WATCHLIST".center(50))
    print("="*50 + "\n")
    
    # Generate recommendations
    watchlist, warning = advisor.generate_watchlist()
    
    if warning:
        print(warning + "\n")
    
    print(watchlist.to_string(index=False))
    
    # Show trading calendar
    print("\n📅 TRADING CALENDAR")
    print(pd.DataFrame(advisor.get_trading_calendar()).to_string(index=False))
    
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
