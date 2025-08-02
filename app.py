"""Astro-Trading Dashboard with Sample Data"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def get_sample_transit_data():
    """Generate sample planetary transit data"""
    data = {
        "Planet": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
        "Time": ["00:00:00"]*7,
        "Motion": ["D", "D", "D", "R", "D", "D", "D"],
        "Zodiac": ["Capricorn", "Gemini", "Gemini", "Sagittarius", "Pisces", "Capricorn", "Aquarius"],
        "Degree": [280, 60, 75, 240, 350, 290, 320],
        "Nakshatra": ["Uttara Ashadha", "Ardra", "Punarvasu", "Purva Ashadha", "Revati", "Uttara Ashadha", "Purva Bhadrapada"],
        "Pada": [4, 1, 1, 3, 4, 4, 2],
        "Declination": [0.0]*7
    }
    return pd.DataFrame(data)

def create_plot(transits):
    """Create and configure the polar plot"""
    fig = go.Figure()
    
    # Add planetary traces
    for _, row in transits.iterrows():
        fig.add_trace(
            go.Scatterpolar(
                r=[row["Degree"]],
                theta=[row["Zodiac"]],
                name=row["Planet"],
                marker=dict(
                    size=20,
                    color="red" if row["Motion"] == "R" else "blue",
                    line=dict(width=2, color="DarkSlateGrey")
                ),
                hovertemplate=(
                    f"<b>{row['Planet']}</b><br>"
                    f"Zodiac: {row['Zodiac']}<br>"
                    f"Degree: {row['Degree']}°<br>"
                    f"Nakshatra: {row['Nakshatra']} (Pada {row['Pada']})<br>"
                    f"Motion: {'Retrograde' if row['Motion'] == 'R' else 'Direct'}"
                    "<extra></extra>"
                )
            )
        )
    
    # Configure layout in separate steps for clarity
    polar_config = dict(
        angularaxis=dict(
            direction="clockwise",
            rotation=90,
            period=360,
            tickvals=list(range(0, 360, 30))
        ),
        radialaxis=dict(visible=False)
    )
    
    fig.update_layout(
        polar=polar_config,
        showlegend=True,
        height=500
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Astro-Trading Dashboard",
        layout="wide",
        page_icon="♋",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌌 Planetary Transit Visualization")
    
    transits = get_sample_transit_data()
    
    if not transits.empty:
        st.plotly_chart(
            create_plot(transits), 
            use_container_width=True
        )
        st.subheader("Planetary Transit Data")
        st.dataframe(transits, use_container_width=True)
    else:
        st.warning("No transit data available")

if __name__ == "__main__":
    main()
