# Prime Condies: A Climber's Weather Hub

Prime Condies is a web app that allows climbers to check conditions and forecasts at climbing locations across the US. Users can select multiple locations to view conditions simultaneously; and you can customize your own preferences for conditions (temperature, humidity, and chance of precipitation).

Try it out for yourself at https://prime-condies.streamlit.app/

## Under the Hood

Prime Condies is a `streamlit` app which runs on [Streamlit Community Cloud](https://streamlit.io/cloud). It accesses the [National Weather Service's API](https://www.weather.gov/documentation/services-web-api) to retrieve forecast data.

## Development Status 

This is an early, unstable, and barely useful iteration of this app -- this is more or less just a wireframe that proves that I can retrieve the necessary data, assess conditions, and plot something. This should take shape over the next several weeks. 

### Current Features

* Location selection from OpenBeta's static dataset
* User-specified preferences for ideal and acceptable conditions
* Retrieve hourly and daily forecast for all selected locations
* Show current conditions for selected locations as a heads-up summary
* Plot hourly and daily condition outlook as a heatmap

### Still To Do

* Clean up Current Conditions display (maybe a table instead?)
* Probably figure out a good way to move the colorbar to the bottom and set `use_container_width=True` in `st.plotly_graph`
* Dewpoint condition (refer to https://www.weather.gov/arx/why_dewpoint_vs_humidity for cutoffs)
  * Would need to rework the cutoff levels which assume an odd number of conditions
* Optional detailed plot of temp/humidity/precip for a given area (below the condition forecast)
* Determine cutoffs based on historical observations in Chattanooga 

### Unknown / Needs Refinement / Long Term

* Is there a better way of aggregating daily info than using the highs?
  * Maybe a count of hours where `condition_score > 0`? In other words, X hours with acceptable conditions
  * Could also use this for the Current Conditions section
* Is there a good way to pull forecasted air quality?
* When it last rained at a location
* Estimate rock temperature