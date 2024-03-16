import streamlit as st 
import pandas as pd
import numpy as np
from src.utils import ClimbingLocation, Condition, aggregate_conditions
import src.plotly_graphs as plot

st.set_page_config(page_title="Prime Condies: A Weather Tool for Climbers", page_icon=":man_climbing:")
st.title("Prime Condies")
st.write("Welcome to Prime Condies, a simple app for climbing conditions. Get psyched :the_horns:")

all_areas = pd.read_csv('data/climbing_locations.csv')
selected_areas = st.multiselect("Select climbing areas", 
                                options=all_areas['composite_name'], max_selections=10, help="Locations taken from Mountain Project hierarchy. If you can't find your crag, try a higher-level grouping from MP.",
                                default=['TN > Dayton Pocket/Laurel Falls Bouldering', 'GA > Rocktown', 'TN > Middle Creek', 'TN > Foster Falls']
                                )
if len(selected_areas) == 0:
    st.warning("Please select one or more climbing destinations to get started")
else:
    # condition details hidden in expander
    with st.expander("Configure condition preferences"):
        st.markdown(
            """
            Use these options to select ideal and acceptable conditions.
            - **Ideal** conditions describe the best case scenario; if all conditions are ideal at once, you definitely want to be climbing
            - **Acceptable** conditions are less preferred than the ideal values, but you would still climb in them
            - Anything outside of the acceptable conditions values should be considered deal-breakers; if _any_ condition is unacceptable, you won't go
            """
        )

        # temperature first: min/max ranges
        st.write("#### Temperature Ranges")
        acceptable_min_temp, acceptable_max_temp = st.slider("Acceptable temperature (&deg;F)", min_value=0, max_value=100, value=(30, 80))
        ideal_min_temp, ideal_max_temp = st.slider("Ideal temperature (&deg;F)", min_value=0, max_value=100, value=(40, 65))
        temperature = Condition(acceptable_low=acceptable_min_temp, acceptable_high=acceptable_max_temp, ideal_low=ideal_min_temp, ideal_high=ideal_max_temp)

        # humidity: max only
        st.write("#### Relative Humidity")
        acceptable_max_humidity = st.slider("Acceptable max humidity", min_value=0, max_value=100, value=70)
        ideal_max_humidity = st.slider("Ideal max humidity", min_value=0, max_value=100, value=50)
        humidity = Condition(acceptable_low=0, acceptable_high=acceptable_max_humidity, ideal_low=0, ideal_high=ideal_max_humidity)

        # dewpoint: max only
        # references:
        # [1] https://www.weather.gov/arx/why_dewpoint_vs_humidity (< 55 is dry and comfortable)
        # [2] https://medium.com/@loukusa/science-friction-62058792d565 (above 60 is too bad to climb)
        st.write("#### Dewpoint")
        acceptable_max_dewpoint = st.slider("Acceptable max dewpoint (&deg;F)", min_value=0, max_value=100, value=55)
        ideal_max_dewpoint = st.slider("Ideal max dewpoint (&deg;F)", min_value=0, max_value=100, value=40)
        dewpoint = Condition(acceptable_low=0, acceptable_high=acceptable_max_dewpoint, ideal_low=0, ideal_high=ideal_max_dewpoint)

        # precip chance: max only
        st.write("#### Chance of Precipitation")
        acceptable_max_precip = st.slider("Acceptable max precipitation chance", min_value=0, max_value=100, value=40)
        ideal_max_precip = st.slider("Ideal max precipitation chance", min_value=0, max_value=100, value=10)
        precipitation = Condition(acceptable_low=0, acceptable_high=acceptable_max_precip, ideal_low=0, ideal_high=ideal_max_precip)

    # pull everything up front
    locations = {}
    daily_forecasts = {}
    hourly_forecasts = {}
    for area in selected_areas:
        locations[area] = ClimbingLocation(**all_areas.loc[all_areas['composite_name'] == area, ['latitude', 'longitude']].iloc[0])
        daily_forecasts[area] = locations[area].retrieve_12hr_forecast()
        hourly_forecasts[area] = locations[area].retrieve_hourly_forecast()
        daily_forecasts[area].df['area'] = area
        hourly_forecasts[area].df['area'] = area

    # combine all the forecast data across areas
    daily_df = pd.concat([forecast.df for forecast in daily_forecasts.values()])
    hourly_df = pd.concat([forecast.df for forecast in hourly_forecasts.values()])

    # get the bucketing based on condition ranges
    daily_df['humidity_condition'] = daily_df['humidity'].apply(humidity.assess)
    daily_df['precipitation_condition'] = daily_df['precipitation'].apply(precipitation.assess)
    daily_df['temperature_condition'] = daily_df['temperature'].apply(temperature.assess)
    daily_df['condition_score'] = daily_df.apply(lambda x: aggregate_conditions(x['humidity_condition'], x['precipitation_condition'], x['temperature_condition']), axis=1)

    hourly_df['humidity_condition'] = hourly_df['humidity'].apply(humidity.assess)
    hourly_df['precipitation_condition'] = hourly_df['precipitation'].apply(precipitation.assess)
    hourly_df['temperature_condition'] = hourly_df['temperature'].apply(temperature.assess)
    hourly_df['dewpoint_condition'] = hourly_df['dewpoint_f'].apply(dewpoint.assess)
    hourly_df['condition_score'] = hourly_df.apply(lambda x: aggregate_conditions(x['humidity_condition'], x['precipitation_condition'], x['temperature_condition'], x['dewpoint_condition']), axis=1)
    hourly_df['hour'] = hourly_df['startTime'].dt.hour
    hourly_df['forecast_period'] = hourly_df['startTime'].dt.strftime("%m/%d") + np.where((hourly_df['hour'] >= 8) & (hourly_df['hour'] < 20), "", " Night")

    # convert condition results to emojis for the current condition readout
    condition_to_emoji = {
        'Ideal': ':white_check_mark:',
        'Acceptable': ':ok:',
        'Unacceptable': ':no_entry_sign:' # or :bricks: or :poop:
    }
    st.write(
        f"""
        ## Current Conditions: What's Good Now
        This section shows you what's happening now at each area. You can tweak
        specific cutoffs in the collapsed menu just above this section, but for reference:
        - {condition_to_emoji['Ideal']} indicates an ideal value for a particular condition
        - {condition_to_emoji['Acceptable']} indicates acceptable conditions
        - {condition_to_emoji['Unacceptable']} indicates unacceptable conditions
        """
    )

    # use the first hourly forecast entry for each area for current conditions (it's the current hour at the time of the request)
    current_df = hourly_df.query("number == 1")[['area', 'temperature', 'humidity', 'precipitation', 'dewpoint_f',
                                                'temperature_condition', 'humidity_condition', 'precipitation_condition', 
                                                'dewpoint_condition', 'shortForecast']].set_index("area")
    
    next_24h = hourly_df.query("number <= 24")\
        .groupby("area")\
        .agg(good_hours = ('condition_score', lambda x: sum(x>0)))

    # write the current conditions as a table ordered by the number of good hours in the next daay
    current_df['temperature_text'] = current_df['temperature'].astype(str) + "&deg;F " + current_df['temperature_condition'].map(condition_to_emoji)
    current_df['dewpoint_text'] = current_df['dewpoint_f'].astype(int).astype(str) + "&deg;F " + current_df['dewpoint_condition'].map(condition_to_emoji)
    current_df['humidity_text'] = current_df['humidity'].astype(str) + "% " + current_df['humidity_condition'].map(condition_to_emoji)
    current_df['precipitation_text'] = current_df['precipitation'].astype(str) + "% " + current_df['precipitation_condition'].map(condition_to_emoji)
    current_overview_df = current_df[['temperature_text', 'dewpoint_text', 'humidity_text', 'precipitation_text']]\
        .join(next_24h)\
        .reset_index(drop=False)\
        .sort_values("good_hours", ascending=False)\
        .rename(columns={'temperature_text': 'Temperature', 
                         'dewpoint_text': 'Dewpoint',
                         'humidity_text':'Humidity', 
                         'precipitation_text':'Chance of Precip.', 
                         'good_hours':'Decent Hours in the Next 24hrs',
                         'area':'Location'})
    
    st.markdown(current_overview_df.to_markdown(index=False))

    st.write("## Daily Condition Outlook")
    st.write("""
    The plot below shows the overall condition outlook for each location you've requested. Each 12-hour period (8am-8pm local time)
    has a bar whose height represents the number of overall decent hours, and each section is shaded according to the overall condition 
    quality (darker green = better condies). 
    """)

    st.plotly_chart(plot.plot_daily_bar_chart(hourly_df), use_container_width=True)
    
    st.write("""
    ## Detailed Hourly Forecast
    If you're interested in the actual forecast values for a location, you can view that here. The plot below shows hourly forecast values,
    with overall condition quality represented by the color of the background -- same as above, darker green corresponds to better conditions.
    """)

    detailed_area = st.selectbox("Detailed forecast location", options=selected_areas)
    specific_area_df = hourly_df[hourly_df['area'] == detailed_area].sort_values("number")
    detailed_starting_time = st.selectbox("Select a starting time for the 48-hour plot", specific_area_df['startTime'].unique())
    st.plotly_chart(plot.plot_hourly_forecast_values(specific_area_df[specific_area_df['startTime'] >= detailed_starting_time].iloc[:48]), use_container_width=True)

    with st.expander("About the app"):
        st.write(
            """
            Prime Condies is a totally free app for informational purposes only. Climbing is an inherently dangerous
            activity, and it should be done with caution. 

            Forecast data comes from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api), 
            and climbing location coordinates are taken from OpenBeta (see [OpenBeta GitHub](https://github.com/OpenBeta/climbing-data))
            """
        )