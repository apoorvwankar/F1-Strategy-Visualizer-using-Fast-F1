import streamlit as st
import seaborn as sns
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd

# Page title
st.title("Driver Lap Time Distribution Visualization")

# User inputs
available_years = list(range(2018, 2024))
year = st.selectbox("Select Year", available_years)

# Fetch race names dynamically
try:
    schedule = fastf1.get_event_schedule(year)
    available_races = schedule['EventName'].tolist()
    race = st.selectbox("Select Race", available_races)
except Exception as e:
    st.error(f"Could not fetch race schedule for {year}. Error: {e}")
    st.stop()

session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])

# Button to trigger the visualization
if st.button("Visualize Lap Times"):
    try:
        # Load session data
        session = fastf1.get_session(year, race, session_type)
        session.load()
        st.write(f"Session loaded: {session.event['EventName']} {year} - {session_type}")

        # Get top 10 finishers and their laps
        point_finishers = session.results.DriverNumber[:10]
        if len(point_finishers) == 0:
            st.error("No finishing data available for this session!")
            st.stop()

        driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps().reset_index()

        if driver_laps.empty:
            st.error("No quick laps found for the session!")
            st.stop()

        # Drop rows with missing Compound data and filter out NaN
        driver_laps = driver_laps.dropna(subset=["Compound"])

        # Remove any invalid or unexpected compounds
        valid_compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
        driver_laps = driver_laps[driver_laps["Compound"].isin(valid_compounds)]

        if driver_laps.empty:
            st.error("No valid compound data available after filtering!")
            st.stop()

        # Get drivers in finishing order
        finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]

        # Convert lap times to seconds for Seaborn
        driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

        # Get unique tire compounds from the cleaned data
        available_compounds = driver_laps["Compound"].unique().tolist()

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))

        # Violin plot for distribution
        sns.violinplot(
            data=driver_laps,
            x="Driver",
            y="LapTime(s)",
            hue="Driver",
            inner=None,
            density_norm="area",
            order=finishing_order,
            palette=fastf1.plotting.get_driver_color_mapping(session=session)
        )

        # Swarm plot for actual lap times
        sns.swarmplot(
            data=driver_laps,
            x="Driver",
            y="LapTime(s)",
            order=finishing_order,
            hue="Compound",
            palette=fastf1.plotting.get_compound_mapping(session=session),
            hue_order=available_compounds,  # Only valid compounds
            linewidth=0,
            size=4,
        )

        # Aesthetic adjustments
        ax.set_xlabel("Driver")
        ax.set_ylabel("Lap Time (s)")
        plt.suptitle(f"{session.event['EventName']} {year} - Lap Time Distributions")
        sns.despine(left=True, bottom=True)
        plt.tight_layout()

        # Display plot in Streamlit
        st.pyplot(fig)
        st.success("Lap time distribution visualization loaded successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
