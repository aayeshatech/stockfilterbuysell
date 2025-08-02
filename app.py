"""
Ultra-Lightweight Astro Stock Advisor
- No external dependencies (works with plain Python)
- Instant execution
- Clear text-based output
- Includes retrograde warnings and trading times
"""

from datetime import datetime, timedelta

class AstroStockAdvisor:
    def __init__(self):
        # Current planetary positions (simplified)
        self.current_transits = {
            'retrograde': [
                {'planet': 'Mercury', 'until': '2025-08-16', 'effect': 'Avoid new investments'}
            ],
            'direct': [
                {'planet': 'Sun', 'sign': 'Capricorn', 'sectors': ['Energy', 'Government'], 'nakshatra': 'Uttara Ashadha'},
                {'planet': 'Jupiter', 'sign': 'Pisces', 'sectors': ['Pharma', 'Banking'], 'nakshatra': 'Revati'},
                {'planet': 'Mars', 'sign': 'Gemini', 'sectors': ['Metals', 'Technology'], 'nakshatra': 'Ardra'}
            ]
        }
        
        # Stock database (symbol, sector, nakshatra)
        self.stocks = [
            ('RELIANCE', 'Energy', 'Uttara Ashadha'),
            ('DIVISLAB', 'Pharma', 'Revati'),
            ('TATASTEEL', 'Metals', 'Rohini'),
            ('INFY', 'Technology', 'Hasta'),
            ('TATAPOWER', 'Utilities', 'Purva Bhadrapada')
        ]

    def get_watchlist(self):
        """Generate and display the watchlist"""
        print("\n" + "="*60)
        print("🌟 ASTROLOGICAL STOCK WATCHLIST".center(60))
        print("="*60 + "\n")
        
        # Show retrograde warnings
        self._show_warnings()
        
        # Generate and show recommendations
        self._show_recommendations()
        
        # Show trading calendar
        self._show_trading_times()
        
        print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _show_warnings(self):
        """Display retrograde warnings"""
        print("⚠️ PLANETARY WARNINGS:")
        for planet in self.current_transits['retrograde']:
            print(f"- {planet['planet']} Retrograde: {planet['effect']} until {planet['until']}")
        print()

    def _show_recommendations(self):
        """Display stock recommendations"""
        print("💎 RECOMMENDED STOCKS:")
        print("-"*60)
        print("{:<10} {:<15} {:<10} {:<15} {:<10}".format(
            'Symbol', 'Sector', 'Signal', 'Strength', 'Alignment'))
        print("-"*60)
        
        for symbol, sector, nakshatra in self.stocks:
            for planet in self.current_transits['direct']:
                if sector in planet['sectors']:
                    strength = "STRONG" if nakshatra == planet['nakshatra'] else "moderate"
                    print("{:<10} {:<15} {:<10} {:<15} {:<10}".format(
                        symbol, sector, 'BUY', strength, 
                        f"{planet['planet']} in {planet['nakshatra']}"))
                    break

    def _show_trading_times(self):
        """Display favorable trading times"""
        print("\n⏰ FAVORABLE TRADING TIMES:")
        today = datetime.now()
        print(f"- {today.strftime('%b %d')} 9:30-11:30 AM : Moon trine Jupiter (Good for buying)")
        print(f"- {(today + timedelta(days=2)).strftime('%b %d')} : Venus square Saturn (Avoid trading)")
        print(f"- {(today + timedelta(days=4)).strftime('%b %d')} : Sun conjunct Jupiter (Excellent for investments)")

# Run the advisor
if __name__ == "__main__":
    advisor = AstroStockAdvisor()
    advisor.get_watchlist()
