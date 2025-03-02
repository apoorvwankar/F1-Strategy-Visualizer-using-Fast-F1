import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
from timple.timedelta import strftimedelta
from fastf1.core import Laps

# Page title
st.title("Qualifying Results Overview")

# Fetch available years and races from FastF1 API
@st.cache_data
def get_available_races(year):
    schedule = fastf1.get_event_schedule(year)
    races = schedule['EventName'].unique().tolist()
    return races

available_years = list(range(2018, 2024))

# Dropdowns for parameter selection
year = st.selectbox("Select Year", available_years)
available_races = get_available_races(year)
race = st.selectbox("Select Race", available_races)

# Button to trigger data loading and plotting
if st.button("Load and Visualize Qualifying Results"):
    session = fastf1.get_session(year, race, 'Q')
    session.load()

    drivers = pd.unique(session.laps['Driver'])

    list_fastest_laps = [session.laps.pick_driver(drv).pick_fastest() for drv in drivers]
    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

    team_colors = [fastf1.plotting.get_team_color(lap['Team'], session=session) for _, lap in fastest_laps.iterlaps()]

    # Plot results
    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'], color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)

    lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')
    plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n"
                 f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

    st.pyplot(fig)

    st.success("Qualifying results visualization loaded successfully!")
