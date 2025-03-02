import streamlit as st
import seaborn as sns
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

# Page title
st.title("Team Pace Comparison")

# Selectbox inputs
available_years = list(range(2018, 2024))
year = st.selectbox("Select Year", available_years)

# Fetch available races dynamically
try:
    schedule = fastf1.get_event_schedule(year)
    available_races = schedule['EventName'].tolist()
    race = st.selectbox("Select Race", available_races)
except Exception as e:
    st.error(f"Could not fetch race schedule for {year}. Error: {e}")
    st.stop()

session_type = st.selectbox("Select Session", ['R', 'Q', 'FP1', 'FP2', 'FP3'])

# Button to trigger the plot
if st.button("Compare Team Pace"):
    try:
        # Load session
        session = fastf1.get_session(year, race, session_type)
        session.load()

        # Get quick laps
        laps = session.laps.pick_quicklaps()

        # Convert lap times to seconds for Seaborn
        transformed_laps = laps.copy()
        transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

        # Order teams by median lap time
        team_order = (
            transformed_laps[["Team", "LapTime (s)"]]
            .groupby("Team")
            .median()["LapTime (s)"]
            .sort_values()
            .index
        )

        # Make a color palette associating team names to hex codes
        team_palette = {
            team: fastf1.plotting.get_team_color(team, session=session)
            for team in team_order
        }

        # Create the plot
        fig, ax = plt.subplots(figsize=(15, 10))
        sns.boxplot(
            data=transformed_laps,
            x="Team",
            y="LapTime (s)",
            hue="Team",
            order=team_order,
            palette=team_palette,
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )

        plt.title(f"{session.event['EventName']} {year} - Team Pace Comparison")
        plt.grid(visible=False)
        ax.set(xlabel=None)  # x-label is redundant
        plt.tight_layout()

        # Display plot in Streamlit
        st.pyplot(fig)
        st.success("Team pace comparison loaded successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
