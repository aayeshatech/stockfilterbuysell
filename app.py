"""
Astro Stock Watchlist Generator (Lightweight Version)
- No external dependencies except pandas (which comes with Anaconda)
- Simplified output for better performance
- Built-in error handling
"""

import pandas as pd
from datetime import datetime, timedelta

class AstroStockAdvisor:
    def __init__(self):
        # Planetary sector mappings
        self.planet_sectors = {
            "Sun": ["Energy", "Government"],
            "Moon": ["Shipping", "Retail"],
            "Mars": ["Metals", "Technology"],
            "Jupiter": ["Pharma", "Banking"],
            "Venus": ["Luxury", "Automobiles"],
            "Saturn": ["Utilities", "Real Estate"]
        }
        
        # Sample stock database (replace with your actual data)
        self.stocks_db = [
            {"symbol": "RELIANCE", "sector": "Energy", "nakshatra": "Uttara Ashadha"},
            {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
            {"symbol": "TATASTEEL", "sector": "Metals", "nakshatra": "Rohini"},
            {"symbol": "INFY", "sector": "Technology", "nakshatra": "Hasta"}
        ]
        
        # Current planetary positions (mock data - replace with API in production)
        self.transits = {
            "retrograde": [{"planet": "Mercury", "until": "2025-08-16"}],
            "direct": [
                {"planet": "Sun", "sign": "Capricorn", "nakshatra": "Uttara Ashadha"},
                {"planet": "Jupiter", "sign": "Pisces", "nakshatra": "Revati"}
            ]
        }

    def generate_watchlist(self):
        """Generate recommendations with error handling"""
        try:
            # 1. Check for retrograde warnings
            warnings = []
            for planet in self.transits["retrograde"]:
                warnings.append(f"⚠️ {planet['planet']} Retrograde (Caution until {planet['until']})")
            
            # 2. Find favorable sectors
            favorable_sectors = set()
            for planet in self.transits["direct"]:
                if planet["planet"] in self.planet_sectors:
                    favorable_sectors.update(self.planet_sectors[planet["planet"]])
            
            # 3. Match stocks to favorable sectors
            recommendations = []
            for stock in self.stocks_db:
                if stock["sector"] in favorable_sectors:
                    signal_strength = "Strong" if any(
                        p["nakshatra"] == stock["nakshatra"] 
                        for p in self.transits["direct"]
                    ) else "Moderate"
                    
                    recommendations.append({
                        "Stock": stock["symbol"],
                        "Sector": stock["sector"],
                        "Signal": "BUY",
                        "Strength": signal_strength,
                        "Reason": f"{stock['nakshatra']} alignment"
                    })
            
            return pd.DataFrame(recommendations), warnings
        
        except Exception as e:
            print(f"❌ Error generating watchlist: {str(e)}")
            return pd.DataFrame(), ["Error occurred"]

    def get_trading_times(self):
        """Get favorable trading times without external dependencies"""
        return [
            {"Date": (datetime.now() + timedelta(days=1)).strftime('%b %d'),
             "Period": "Morning",
             "Quality": "Good"},
            {"Date": (datetime.now() + timedelta(days=3)).strftime('%b %d'),
             "Period": "Afternoon",
             "Quality": "Avoid"}
        ]

def main():
    print("\n" + "="*50)
    print("ASTRO STOCK ADVISOR".center(50))
    print("="*50 + "\n")
    
    advisor = AstroStockAdvisor()
    
    # Generate and display watchlist
    watchlist, warnings = advisor.generate_watchlist()
    
    for warning in warnings:
        print(warning)
    
    if not watchlist.empty:
        print("\nRecommended Stocks:")
        print(watchlist.to_string(index=False))
    else:
        print("\nNo recommendations generated")
    
    # Show trading times
    print("\nFavorable Trading Times:")
    print(pd.DataFrame(advisor.get_trading_times()).to_string(index=False))
    
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
