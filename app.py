import pandas as pd
from datetime import datetime, timedelta

# Lightweight planetary analysis (no Plotly)
def generate_watchlist():
    current_transits = {
        "retrograde": [{"planet": "Mercury", "sign": "Sagittarius"}],
        "direct": [
            {"planet": "Jupiter", "sign": "Pisces", "nakshatra": "Revati"}
        ]
    }
    
    stocks = [
        {"symbol": "DIVISLAB", "sector": "Pharma", "nakshatra": "Revati"},
        {"symbol": "RELIANCE", "sector": "Energy", "nakshatra": "Uttara Ashadha"}
    ]
    
    watchlist = []
    for stock in stocks:
        for planet in current_transits["direct"]:
            if planet.get("nakshatra") == stock["nakshatra"]:
                watchlist.append({
                    "Stock": stock["symbol"],
                    "Action": "BUY",
                    "Reason": f"{planet['planet']} in {planet['nakshatra']}"
                })
    
    return pd.DataFrame(watchlist)

# Run and print
print("🚀 Astro Stock Watchlist")
print(generate_watchlist().to_string(index=False))
print(f"\n⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
