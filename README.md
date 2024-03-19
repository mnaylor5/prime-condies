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
* Retrieve hourly forecast for all selected locations
* Show current conditions for selected locations as a table, including how many of the next 24 hours are at least decent according to condition preferences
* Daily plot of aggregate conditions (stacked bar chart of quality hours)
* Hourly plot of actual forecast values with condition value overlaid as background color

### Still To Do

* Figure out better mobile rendering (maybe static plots)
* Clean up OpenBeta dataset

### Unknown / Needs Refinement / Long Term

* Determine cutoffs based on historical observations in Chattanooga?
* Is there a good way to pull forecasted air quality? (not really with free options)
* When it last rained at a location (probably not possible with free options)
* Estimate rock temperature (long term)