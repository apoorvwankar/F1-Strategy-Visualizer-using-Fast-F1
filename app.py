import streamlit as st

# Hide the sidebar navigation
st.set_page_config(page_title="F1 Strategy Visualization", page_icon="🏎️", initial_sidebar_state="collapsed")

# Title
st.title("F1 Strategy Visualization")

# Visualization options
visualizations = {
    "Driver Lap Time Distribution Visualization": "pages/app_driverdist.py",
    "F1 Driver Standings Heatmap": "pages/app_driverstanding.py",
    "Fastest Lap Gear Shift Visualization": "pages/app_gearshift.py",
    "Driver Laptimes Scatterplot": "pages/app_laptime.py",
    "Driver-Specific Lap Time Styling": "pages/app_laptimestyling.py",
    "Qualifying Results Overview": "pages/app_quali.py",
    "F1 Session Data Viewer": "pages/app_session.py",
    "Speed Visualization on Track Map": "pages/app_speedvis.py",
    "Team Pace Comparison": "pages/app_teampace.py",
    "Tyre Strategies During a Race": "pages/app_tyre.py"
}

selected_vis = st.selectbox("Choose a Visualization", list(visualizations.keys()))

# Button to navigate
if st.button("Go to Visualization"):
    st.session_state["selected_vis"] = visualizations[selected_vis]
    st.switch_page(visualizations[selected_vis])  
