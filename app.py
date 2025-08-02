"""
Astro Stock Advisor - Streamlit App
Minimal dependencies version
"""

import streamlit as st
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="Astro Stock Advisor",
    page_icon="✨",
    layout="wide"
)

class AstroAdvisor:
    def __init__(self):
        self.transits = {
            'retrograde': [
                {'planet': 'Mercury', 'until': '2025-08-16', 'effect': 'Avoid new investments'}
            ],
            'direct': [
                {'planet': 'Sun', 'sign': 'Capricorn', 'sectors': ['Energy', 'Government'], 'nakshatra': 'Uttara Ashadha'},
                {'planet': 'Jupiter', 'sign': 'Pisces', 'sectors': ['Pharma', 'Banking'], 'nakshatra': 'Revati'}
            ]
        }
        self.stocks = [
            ('RELIANCE', 'Energy', 'Uttara Ashadha'),
            ('DIVISLAB', 'Pharma', 'Revati'),
            ('TATASTEEL', 'Metals', 'Rohini')
        ]

    def display_watchlist(self):
        """Main display function"""
        st.title("✨ Astrological Stock Watchlist")
        st.divider()
        
        # Show warnings
        self._show_warnings()
        
        # Show recommendations
        self._show_recommendations()
        
        # Show trading times
        self._show_trading_times()
        
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _show_warnings(self):
        """Display retrograde warnings"""
        with st.container(border=True):
            st.subheader("⚠️ Planetary Warnings")
            for planet in self.transits['retrograde']:
                st.warning(
                    f"{planet['planet']} Retrograde: {planet['effect']} until {planet['until']}",
                    icon="⚠️"
                )

    def _show_recommendations(self):
        """Display stock recommendations"""
        with st.container(border=True):
            st.subheader("💎 Recommended Stocks")
            
            # Create columns for better layout
            cols = st.columns([1, 1, 1, 1])
            headers = ["Symbol", "Sector", "Signal", "Strength"]
            for col, header in zip(cols, headers):
                col.write(f"**{header}**")
            
            for symbol, sector, nakshatra in self.stocks:
                for planet in self.transits['direct']:
                    if sector in planet['sectors']:
                        strength = "💎 Strong" if nakshatra == planet['nakshatra'] else "🔹 Moderate"
                        cols = st.columns([1, 1, 1, 1])
                        cols[0].code(symbol)
                        cols[1].write(sector)
                        cols[2].success("BUY")
                        cols[3].write(strength)
                        break

    def _show_trading_times(self):
        """Display favorable trading times"""
        with st.container(border=True):
            st.subheader("⏰ Favorable Trading Times")
            today = datetime.now()
            
            st.markdown("""
            | Date       | Time         | Quality       | Reason                     |
            |------------|--------------|---------------|----------------------------|
            | {date1} | 9:30-11:30 AM | ✅ Favorable  | Moon trine Jupiter        |
            | {date2} | All day       | ❌ Avoid      | Venus square Saturn       |
            | {date3} | Afternoon     | ⭐ Excellent  | Sun conjunct Jupiter      |
            """.format(
                date1=today.strftime('%b %d'),
                date2=(today + timedelta(days=2)).strftime('%b %d'),
                date3=(today + timedelta(days=4)).strftime('%b %d')
            ))

# Run the app
if __name__ == "__main__":
    advisor = AstroAdvisor()
    advisor.display_watchlist()
