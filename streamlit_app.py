import streamlit as st 
import pandas as pd
from src.utils import ClimbingLocation, Condition, aggregate_conditions
import src.plotly_graphs as plot

st.set_page_config(page_title="Prime Condies: A Weather Tool for Climbers", page_icon=":man_climbing:")
st.title("Prime Condies")
st.write("Welcome to Prime Condies, a simple app for climbing conditions. Get psyched :the_horns:")

all_areas = pd.read_csv('data/climbing_locations.csv')
selected_areas = st.multiselect("Select climbing areas for forecasts (taken from MP hierarchy)", 
                                options=all_areas['composite_name'], max_selections=10, 
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
        acceptable_min_temp, acceptable_max_temp = st.slider("Acceptable temperature (F)", min_value=0, max_value=100, value=(30, 80))
        ideal_min_temp, ideal_max_temp = st.slider("Ideal temperature (F)", min_value=0, max_value=100, value=(40, 65))
        temperature = Condition(acceptable_low=acceptable_min_temp, acceptable_high=acceptable_max_temp, ideal_low=ideal_min_temp, ideal_high=ideal_max_temp)

        # humidity: max only
        acceptable_max_humidity = st.slider("Acceptable max humidity", min_value=0, max_value=100, value=70)
        ideal_max_humidity = st.slider("Ideal max humidity", min_value=0, max_value=100, value=50)
        humidity = Condition(acceptable_low=0, acceptable_high=acceptable_max_humidity, ideal_low=0, ideal_high=ideal_max_humidity)

        # precip chance: max only
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
    hourly_df['condition_score'] = hourly_df.apply(lambda x: aggregate_conditions(x['humidity_condition'], x['precipitation_condition'], x['temperature_condition']), axis=1)
    hourly_df['hour'] = hourly_df['startTime'].dt.hour

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
    current_df = hourly_df.query("number == 1")[['area', 'temperature', 'humidity', 'precipitation', 
                                                'temperature_condition', 'humidity_condition', 'precipitation_condition', 'shortForecast']].set_index("area")
    
    next_24h = hourly_df.query("number <= 24")\
        .groupby("area")\
        .agg(good_hours = ('condition_score', lambda x: sum(x>0)))

    # write the current conditions
    current_columns = st.columns(2)
    for i, area in enumerate(selected_areas):
        area_row = current_df.loc[area]
        with current_columns[i % 2]:
            st.markdown(            
                f"""
                ##### {area}
                {area_row['shortForecast']}
                - {area_row['temperature']}&deg;F {condition_to_emoji[area_row['temperature_condition']]}
                - {area_row['humidity']}% humidity {condition_to_emoji[area_row['humidity_condition']]}
                - {area_row['precipitation']}% precipitation {condition_to_emoji[area_row['precipitation_condition']]}
                - {next_24h.loc[area, 'good_hours']} of the next 24 hours are at least decent
                """
            )

    st.write("## Condition Outlook")
    st.write("""
    Use the radio button to select whether you want to see forecasts by hour or by 12-hour blocks. Hourly forecasts will be more detailed,
    while daily uses the highs (during daytime) and lows (at night). The forecasts will appear as a heatmap grid of areas and time periods, 
    where each entry is shaded according to the overall condition quality (darker green = better condies). 
    """)
    forecast_selection = st.radio("Forecast detail", options=["Hourly", "Daily"])
        

    if forecast_selection == 'Daily':
        daytime_only = st.checkbox("Daytime hours only?", value=True)
        st.plotly_chart(plot.plot_daily_heatmap(daily_df, filter_to_daytime=daytime_only))
    else:
        col1, col2 = st.columns(2)
        with col1:
            starting_time = st.selectbox("Select starting point for hourly forecast", options=hourly_df['startTime'].unique())
        with col2:
            hourly_periods = st.number_input("Hourly periods to plot", value=hourly_df['number'].max(), min_value=12, max_value=hourly_df['number'].max())

        hourly_plot_df = hourly_df[
            hourly_df['startTime'] >= starting_time
        ]
        
        st.plotly_chart(plot.plot_hourly_heatmap(hourly_plot_df, periods=hourly_periods))

        st.write("Note: You can click and drag horizontally to zoom to a particular time period on this plot. Double-click to reset.")

    with st.expander("About the app"):
        st.write(
            """
            Prime Condies is a totally free app for informational purposes only. Climbing is an inherently dangerous
            activity, and it should be done with caution. 

            Forecast data comes from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api), 
            and climbing location coordinates are taken from OpenBeta (see [OpenBeta GitHub](https://github.com/OpenBeta/climbing-data))
            """
        )