import streamlit as st
import pandas as pd
import plotly.express as px
from fastf1.ergast import Ergast

# Streamlit app title
st.title("F1 Driver Standings Heatmap")

# Year selection
year = st.selectbox("Select Season", list(range(2018, 2024)))

# Button to generate heatmap
if st.button("Generate Heatmap"):
    try:
        ergast = Ergast()
        races = ergast.get_race_schedule(year)
        results = []

        # Debug race schedule
        st.write("Race Schedule:", races)

        # Fetch results for each race
        for rnd, race in races['raceName'].items():
            try:
                temp = ergast.get_race_results(season=year, round=rnd + 1)
                temp = temp.content[0]

                # Handle sprint races
                sprint = ergast.get_sprint_results(season=year, round=rnd + 1)
                if sprint.content and sprint.description['round'][0] == rnd + 1:
                    temp = pd.merge(temp, sprint.content[0], on='driverCode', how='left')
                    temp['points'] = temp['points_x'] + temp['points_y']
                    temp.drop(columns=['points_x', 'points_y'], inplace=True)

                # Add race info
                temp['round'] = rnd + 1
                temp['race'] = race.removesuffix(' Grand Prix')
                temp = temp[['round', 'race', 'driverCode', 'points']]

                results.append(temp)

            except Exception as race_error:
                st.warning(f"Skipping {race} due to an error: {race_error}")

        # Combine results
        if not results:
            st.error("No race results found!")
            st.stop()

        results = pd.concat(results)
        st.write("Results DataFrame:", results)

        # Pivot results
        results = results.pivot(index='driverCode', columns='round', values='points')
        results['total_points'] = results.sum(axis=1)
        results = results.sort_values(by='total_points', ascending=False)
        results.drop(columns='total_points', inplace=True)

        races = results.columns
        results.columns = races

        # Debugging outputs
        st.write("Final Results Table:", results)

        # Plot heatmap
        fig = px.imshow(
            results,
            text_auto=True,
            aspect='auto',
            color_continuous_scale=[[0, 'rgb(198, 219, 239)'],
                                    [0.25, 'rgb(107, 174, 214)'],
                                    [0.5, 'rgb(33, 113, 181)'],
                                    [0.75, 'rgb(8, 81, 156)'],
                                    [1, 'rgb(8, 48, 107)']],
            labels={'x': 'Race', 'y': 'Driver', 'color': 'Points'}
        )
        fig.update_xaxes(title_text='', side='top')
        fig.update_yaxes(title_text='', tickmode='linear', showgrid=True, gridcolor='LightGrey')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False, margin=dict(l=0, r=0, b=0, t=0))

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
