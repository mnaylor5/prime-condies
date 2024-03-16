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
* Show current conditions for selected locations as a table, including how many of the next 24 hours are at least decent according to condition preferences
* Daily plot of aggrergate conditions (stacked bar chart of quality hours)
* Hourly plot of actual forecast values with condition value behind (darker green = better)

### Still To Do

* Word wrapping long destination names on the heatmaps (possibly just manually add `<br>` tags at regular intervals)
* Probably figure out a good way to move the colorbar to the bottom and set `use_container_width=True` in `st.plotly_graph`

### Unknown / Needs Refinement / Long Term

* Is there a better way of aggregating daily info than using the highs?
  * Maybe a count of hours where `condition_score > 0`? In other words, X hours with acceptable conditions
* Determine cutoffs based on historical observations in Chattanooga?
* Is there a good way to pull forecasted air quality?
* When it last rained at a location
* Estimate rock temperature