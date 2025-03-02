import streamlit as st
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import fastf1 as ff1

# Page title
st.title("Speed Visualization on Track Map")

# Inputs for year, weekend, session, and driver
year = st.number_input("Select Year", min_value=2018, max_value=2024, value=2021)
weekend = st.number_input("Select Weekend Number", min_value=1, max_value=23, value=9)
session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])
driver = st.text_input("Enter Driver Abbreviation (e.g., VER, HAM, RIC)")

colormap = mpl.cm.plasma

# Button to trigger data loading and plotting
if st.button("Load and Visualize Speed Map"):
    try:
        session = ff1.get_session(year, weekend, session_type)
        weekend_event = session.event
        session.load()

        lap = session.laps.pick_driver(driver).pick_fastest()

        # Get telemetry data
        x = lap.telemetry['X']
        y = lap.telemetry['Y']
        color = lap.telemetry['Speed']

        # Create line segments for coloring
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Plotting
        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        fig.suptitle(f'{weekend_event.name} {year} - {driver} - Speed', size=24, y=0.97)

        # Adjust margins and turn off axis
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')

        # Background track line
        ax.plot(x, y, color='black', linestyle='-', linewidth=16, zorder=0)

        # Line collection for speed color mapping
        norm = plt.Normalize(color.min(), color.max())
        lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
        lc.set_array(color)
        line = ax.add_collection(lc)

        # Colorbar legend
        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
        legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")

        st.pyplot(fig)
        st.success("Speed visualization loaded successfully!")

    except Exception as e:
        st.error(f"An error occurred: {e}")