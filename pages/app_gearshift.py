import streamlit as st
import fastf1
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import colormaps

# Page title
st.title("Fastest Lap Gear Shift Visualization")

# User inputs for year, race, session, and driver
available_years = list(range(2018, 2024))
available_races = ['Austrian Grand Prix', 'British Grand Prix', 'Italian Grand Prix', 'Monaco Grand Prix']

year = st.selectbox("Select Year", available_years)
race = st.selectbox("Select Race", available_races)
session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])
driver = st.text_input("Enter Driver Abbreviation (e.g., VER, HAM, LEC)")

# Button to trigger visualization
if st.button("Visualize Gear Shifts"):
    try:
        session = fastf1.get_session(year, race, session_type)
        session.load()

        # Get fastest lap for the specified driver
        lap = session.laps.pick_driver(driver).pick_fastest()
        if lap is None:
            st.error(f"No fastest lap data found for driver {driver}!")
        else:
            tel = lap.get_telemetry()

            if tel.empty:
                st.error(f"No telemetry data available for driver {driver} in this session!")
            else:
                # Prepare data for plotting
                x = np.array(tel['X'].values)
                y = np.array(tel['Y'].values)
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                gear = tel['nGear'].to_numpy().astype(float)

                # Create line collection
                cmap = colormaps['Paired']
                lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
                lc_comp.set_array(gear)
                lc_comp.set_linewidth(4)

                # Plot
                fig, ax = plt.subplots()
                ax.add_collection(lc_comp)
                ax.axis('equal')
                ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

                plt.suptitle(f"Fastest Lap Gear Shift Visualization\n{driver} - {session.event['EventName']} {session.event.year}")

                # Add colorbar
                cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
                cbar.set_ticks(np.arange(1.5, 9.5))
                cbar.set_ticklabels(np.arange(1, 9))

                # Show plot in Streamlit
                st.pyplot(fig)
                st.success("Gear shift visualization loaded successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
