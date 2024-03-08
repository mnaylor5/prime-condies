# Prime Condies: A Climber's Weather Hub

Prime Condies is a web app that allows climbers to check conditions and forecasts at climbing locations across the US. Users can select multiple locations to view conditions simultaneously; and you can customize your own preferences for conditions (temperature, humidity, and chance of precipitation).

Try it out for yourself at https://prime-condies.streamlit.app/

## Under the Hood

Prime Condies is a `streamlit` app which runs on [Streamlit Community Cloud](https://streamlit.io/cloud). It accesses the [National Weather Service's API](https://www.weather.gov/documentation/services-web-api) to retrieve forecast data.

## Development Status 

This is an early, unstable, and barely useful iteration of this app -- this is more or less just a wireframe that proves that I can retrieve the necessary data, assess conditions, and plot something. This should take shape over the next several weeks. 

### Work in Progress

* Refine condition aggregation into a composite value to assess each time period -- will drive coloring/recommendations

### Current Features

* Selection from a handful of predefined locations
* User-specified preferences for ideal and acceptable conditions
* Retrieve hourly and daily forecast for all selected locations
* Show current conditions for selected locations as a heads-up summary
* Plot daily condition outlook as a heatmap

### Still To Do

* Figure out what to do with the hourly forecasts
  * Limit to 48 hour periods? Could follow something like [this](https://forecast.weather.gov/MapClick.php?lat=35.0458&lon=-85.2704&unit=0&lg=english&FcstType=graphical)
  * Color sections that are ideal or acceptable
  * Could also have a time filter to clean this up
* Color-coding plots based on overall view of condition 
* Pulling climbing areas from OpenBeta

### Unknown / Needs Refinement / Long Term

* When it last rained at a location
* Something with dewpoint 
* Estimate rock temperature