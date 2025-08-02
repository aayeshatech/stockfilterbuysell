"""Astro-Trading Dashboard with Sample Data"""
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# First install required packages by running:
# pip install streamlit pandas plotly

# Sample planetary data
def get_sample_transit_data():
    """Generate sample planetary transit data"""
    return pd.DataFrame([
        ["Sun", "00:00:00", "D", "Capricorn", 280, "Uttara Ashadha", 4, 0.0],
        ["Moon", "00:00:00", "D", "Gemini", 60, "Ardra", 1, 0.0],
        ["Mars", "00:00:00", "D", "Gemini", 75, "Punarvasu", 1, 0.0],
        ["Mercury", "00:00:00", "R", "Sagittarius", 240, "Purva Ashadha", 3, 0.0],
        ["Jupiter", "00:00:00", "D", "Pisces", 350, "Revati", 4, 0.0],
        ["Venus", "00:00:00", "D", "Capricorn", 290, "Uttara Ashadha", 4, 0.0],
        ["Saturn", "00:00:00", "D", "Aquarius", 320, "Purva Bhadrapada", 2, 0.0]
    ], columns=[
        "Planet", "Time", "Motion", "Zodiac", "Degree", 
        "Nakshatra", "Pada", "Declination"
    ])

def plot_planetary_positions(transits: pd.DataFrame):
    """Create polar plot of planetary positions"""
    fig = go.Figure()
    
    for _, row in transits.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["Degree"]],
            theta=[row["Zodiac"]],
            name=row["Planet"],
            marker=dict(
                size=20,
                color="red" if row["Motion"] == "R" else "blue",
                line=dict(width=2, color="DarkSlateGrey")
            ),
            hovertemplate=f"<b>{row['Planet']}</b><br>"
                        f"Zodiac: {row['Zodiac']}<br>"
                        f"Degree: {row['Degree']}°<br>"
                        f"Nakshatra: {row['Nakshatra']} (Pada {row['Pada']})<br>"
                        f"Motion: {'Retrograde' if row['Motion'] == 'R' else 'Direct'}<extra></extra>"
        ))
    
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                period=360,
                tickvals=list(range(0, 360, 30))
        ),
        radialaxis=dict(visible=False),
        showlegend=True,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Astro-Trading Dashboard",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌌 Planetary Transit Visualization")
    
    # Get sample data
    transits = get_sample_transit_data()
    
    if not transits.empty:
        plot_planetary_positions(transits)
        st.subheader("Planetary Transit Data")
        st.dataframe(transits, use_container_width=True)
    else:
        st.warning("No transit data available")

if __name__ == "__main__":
    main()
