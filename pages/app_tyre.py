import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# Page title
st.title("Tyre Strategies During a Race")

# Fetch available years and races from FastF1 API
@st.cache_data
def get_available_races(year):
    schedule = fastf1.get_event_schedule(year)
    races = schedule['EventName'].unique().tolist()
    return races

available_years = list(range(2018, 2024))  # Example range of years

# Dropdowns for parameter selection
year = st.selectbox("Select Year", available_years)
available_races = get_available_races(year)
race = st.selectbox("Select Race", available_races)
session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])

# Load the race session
@st.cache_data
def load_race_data(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load()
    return session

# Button to trigger data loading and plotting
if st.button("Load and Visualize Tyre Strategy"):
    session = load_race_data(year, race, session_type)
    laps = session.laps

    # Get driver abbreviations
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]

    # Calculate stints
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})

    # Plot strategies
    fig, ax = plt.subplots(figsize=(5, 10))

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]
        previous_stint_end = 0
        for _, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
            plt.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black",
                fill=True
            )
            previous_stint_end += row["StintLength"]

    # Final plot adjustments
    plt.title(f"{year} {race} Strategies")
    plt.xlabel("Lap Number")
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.tight_layout()

    # Show plot in Streamlit
    st.pyplot(fig)

    st.success("Tyre strategy visualization loaded successfully!")
