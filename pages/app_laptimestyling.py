import streamlit as st
from matplotlib import pyplot as plt
import fastf1
from fastf1 import plotting

# Page title
st.title("Driver-Specific Lap Time Styling")

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
if st.button("Visualize Driver Lap Times"):
    try:
        # Load session data
        session = fastf1.get_session(year, race, session_type)
        session.load()
        st.write(f"Session loaded: {session.event['EventName']} {year} - {session_type}")

        # Select drivers — let’s grab the top 5 finishers for simplicity
        point_finishers = session.results.DriverNumber[:5]
        driver_abbreviations = [session.get_driver(i)["Abbreviation"] for i in point_finishers]

        if len(driver_abbreviations) == 0:
            st.error("No finishing data available for this session!")
            st.stop()

        # Setup FastF1 dark color scheme and timedelta support
        plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')

        # Custom styling for drivers
        custom_styles = [
            {'color': 'auto', 'linestyle': 'solid', 'linewidth': 5, 'alpha': 0.3},  # First driver style
            {'color': 'auto', 'linestyle': 'solid', 'linewidth': 1, 'alpha': 0.7}   # Second driver style
        ]

        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 5))

        for idx, driver in enumerate(driver_abbreviations):
            laps = session.laps.pick_driver(driver).pick_quicklaps().reset_index()

            if laps.empty:
                st.warning(f"No valid lap data for {driver}")
                continue

            # Apply custom driver styles
            style = plotting.get_driver_style(identifier=driver, style=custom_styles, session=session)
            ax.plot(laps['LapNumber'], laps['LapTime'], **style, label=driver)

        # Add axis labels and a sorted legend
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time")
        plotting.add_sorted_driver_legend(ax, session)

        # Display the plot in Streamlit
        st.pyplot(fig)
        st.success("Driver-specific lap time plot loaded successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
