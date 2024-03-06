import streamlit as st 
import pandas as pd
from utils import DEFAULT_LOCATIONS, ClimbingLocation, Condition, aggregate_conditions
import plotly_graphs as plot

st.set_page_config(page_title="Prime Condies: A Weather Tool for Climbers", page_icon=":man_climbing:")
st.title("Prime Condies")
st.write("Welcome to Prime Condies, a simple app for climbing conditions. Get psyched :the_horns:")

selected_areas = st.multiselect("Select climbing areas for forecasts", 
                                options=DEFAULT_LOCATIONS.keys(), default=['Dayton Pocket', 'Rocktown', 'Upper Middle Creek', "Joe's Valley"])

# condition details hidden in expander
with st.expander("Configure condition preferences"):
    st.markdown(
        """
        Use these options to select ideal and acceptable conditions.
        - **Ideal** conditions describe the best case scenario; if all conditions are ideal at once, you definitely want to be climbing.
        - **Unacceptable** conditions should be considered deal-breakers; if _any_ condition is unacceptable, you won't go.
        - Anything between unacceptable and ideal is considered acceptable or decent enough to go as long as other conditions are decent.
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


locations = {}
daily_forecasts = {}
hourly_forecasts = {}
for area in selected_areas:
    locations[area] = ClimbingLocation(*DEFAULT_LOCATIONS[area])
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
daily_df['overall'] = daily_df.apply(lambda x: aggregate_conditions(x['humidity_condition'], x['precipitation_condition'], x['temperature_condition']), axis=1)

hourly_df['humidity_condition'] = hourly_df['humidity'].apply(humidity.assess)
hourly_df['precipitation_condition'] = hourly_df['precipitation'].apply(precipitation.assess)
hourly_df['temperature_condition'] = hourly_df['temperature'].apply(temperature.assess)
hourly_df['overall'] = hourly_df.apply(lambda x: aggregate_conditions(x['humidity_condition'], x['precipitation_condition'], x['temperature_condition']), axis=1)

st.write("## Current Conditions")
st.dataframe(hourly_df.query("number == 1")[['area', 'overall', 'temperature', 'humidity', 'precipitation', 'temperature_condition', 'humidity_condition', 'precipitation_condition', 'shortForecast']], hide_index=True)

st.write("## Forecasts")
st.write("Use the radio button to select whether you want to see forecasts by hour or by 12-hour blocks. Daily will give you a better sense of larger blocks of time, while hourly will be more detailed. You can also choose to filter to daytime hours only.")
col1, col2 = st.columns(2)
with col1:
    forecast_selection = st.radio("Forecast detail", options=["Daily", "Hourly"])
with col2:
    daytime_only = st.checkbox("Daytime hours only?", value=True)

if forecast_selection == 'Daily':
    st.plotly_chart(plot.plot_daily_forecast(daily_df, filter_to_daytime=daytime_only))

with st.expander("About the app"):
    st.write(
        """
        Prime Condies is a totally free app for informational purposes only. Climbing is an inherently dangerous
        activity, and it should be done with caution. 

        Forecast data comes from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api), 
        and climbing location coordinates are taken from OpenBeta (see [OpenBeta GitHub](https://github.com/OpenBeta/climbing-data))
        """
    )