import streamlit as st
import fastf1 as ff1

# Enable FastF1 cache
ff1.Cache.enable_cache('fastf1_cache')

st.title("F1 Session Data Viewer")

# Sidebar inputs
season = st.number_input("Select Season", min_value=1996, max_value=2024, value=2021)
round_number = st.number_input("Select Round", min_value=1, max_value=23, value=15)
session_type = st.selectbox("Select Session Type", ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R'], index=5)

if st.button("Load Session Data"):
    with st.spinner("Loading session data..."):
        try:
            # Get session
            session = ff1.get_session(season, round_number, session_type)
            session.load()

            # Get laps
            laps = session.laps

            if laps.empty:
                st.warning("No lap data available for this session.")
            else:
                st.success(f"Loaded data for {session.event['EventName']} {season}")
                st.dataframe(laps.head())

        except Exception as e:
            st.error(f"Failed to load session data: {e}")
