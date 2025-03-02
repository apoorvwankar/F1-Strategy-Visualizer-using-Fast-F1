import streamlit as st
import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt

# Page title
st.title("Driver Laptimes Scatterplot")

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
session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])
driver = st.text_input("Enter Driver Code (e.g., ALO)")

# Button to trigger data loading and plotting
if st.button("Load and Visualize Driver Laptimes"):
    session = fastf1.get_session(year, race, session_type)
    session.load()

    driver_laps = session.laps.pick_driver(driver).pick_quicklaps().reset_index()

    # Plot laptimes
    fig, ax = plt.subplots(figsize=(8, 8))

    sns.scatterplot(data=driver_laps,
                    x="LapNumber",
                    y="LapTime",
                    ax=ax,
                    hue="Compound",
                    palette=fastf1.plotting.get_compound_mapping(session=session),
                    s=80,
                    linewidth=0,
                    legend='auto')

    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    ax.invert_yaxis()
    plt.suptitle(f"{driver} Laptimes in the {year} {race}")
    plt.grid(color='w', which='major', axis='both')
    sns.despine(left=True, bottom=True)
    plt.tight_layout()

    st.pyplot(fig)

    st.success("Driver laptimes scatterplot loaded successfully!")
