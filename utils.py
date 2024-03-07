# this file contains simple helpers for the weather app
import requests
import json
import pandas as pd
from dataclasses import dataclass
from typing import Union
from collections import Counter

# this group of default locations is mostly for basic functionality 
# until i add location search (much later)
# map location name : (lat, lon)
DEFAULT_LOCATIONS = {
    "Stone Fort (LRC)": (35.2477368,-85.2230326),
    "Joe's Valley": (39.2765, -111.17387),
    "Dayton Pocket": (35.5264821,-85.0242827),
    "Rocktown": (34.6590035,-85.3914826),
    "Little River Canyon": (34.35929, -85.66846),
    "Upper Middle Creek": (35.149630,-85.351334),
    "Woodcock Cove": (35.337004,-85.4532359),
    "Foster Falls": (35.1821082,-85.6754071),
    "Obed (Lilly Boulders)": (36.1026999,-84.7240969)
}

# base class for locations + managing API requests
class ClimbingLocation:
    '''
    Wrapper class for a climbing location -- currently just takes the location's 
    coordinates and handles API requests, but could be extended to include route info
    or other metadata (if a source is available)
    '''
    def __init__(self, latitude, longitude):
        self.latitude = round(latitude, 4) 
        self.longitude = round(longitude, 4)
        self._retrieve_basic_details()

    def _get_request_helper(self, url, current_try=1, max_retries=5):
        'Very simple utility to handle GET requests, check for errors, and decode the response'
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content.decode())
        elif response.status_code == 500:
            body = json.loads(response.content.decode())
            if body['title'] == 'Unexpected Problem':
                # recurse and try it again
                if current_try < max_retries:
                    print(f"Trying {url} again; {current_try} attempt(s) unsuccessful")
                    return self._get_request_helper(url, current_try + 1)
                else:
                    raise ValueError(f"Max retries exceeded for {url}\nLikely an API problem")
        else:
            raise ValueError(f"API Request failed for {url} \n{response.content}")
        

    def _retrieve_basic_details(self):
        # make the get request based on lat/lon
        location_details = self._get_request_helper(f"https://api.weather.gov/points/{self.latitude},{self.longitude}")
        # store the full details in case we need them later
        self.location_metadata = location_details
        # store the forecast URLs 
        self.forecast_urls = {
            '12hr': location_details['properties']['forecast'],
            'hourly': location_details['properties']['forecastHourly']
        }

    def retrieve_12hr_forecast(self):
        return ForecastResponse(self._get_request_helper(self.forecast_urls['12hr']))
    
    def retrieve_hourly_forecast(self):
        return ForecastResponse(self._get_request_helper(self.forecast_urls['hourly']))
    
    def __repr__(self):
        return f"Lat: {self.latitude} // lon: {self.longitude} // forecast URLs: {self.forecast_urls}"
    
class ForecastResponse:
    '''
    Another simple wrapper class to convert the forecast periods to a Pandas dataframe and
    log some additional metadata
    '''
    def __init__(self, forecast_json):
        self.input_json = forecast_json
        self._unroll_periods()
    
    def _unroll_periods(self):
        '''
        The $.properties.periods array is already compatible with Pandas DataFrame
        and is already in tidy format, so we can just pass that along
        '''
        self.df = pd.DataFrame(self.input_json['properties']['periods'])
        self.df['dewpoint_f'] = self.df['dewpoint'].apply(lambda x: x.get("value")).apply(self.convert_celsius_to_fahrenheit)
        self.df['humidity'] = self.df['relativeHumidity'].apply(lambda x: x.get("value"))
        # probability of precipitation comes in with None if there is 0 chance forecasted
        self.df['precipitation'] = self.df['probabilityOfPrecipitation'].apply(lambda x: x.get("value")).fillna(0.0)
        self.start_time = self.df['startTime'].min()
        self.end_time = self.df['endTime'].max()
    
    def convert_celsius_to_fahrenheit(self, x):
        return x * 9/5 + 32
    
    def __repr__(self):
        return f"ForecastResponse from {self.start_time} to {self.end_time} with {self.df.shape[0]} entries"
    
@dataclass
class Condition:
    'A class containing details for a particular condition (temp, humidity, precipitation)'
    acceptable_low: Union[int, float] = None 
    acceptable_high: Union[int, float] = None 
    ideal_low: Union[int, float] = None 
    ideal_high: Union[int, float] = None 

    def assess(self, value):
        if (value < self.acceptable_low) | (value > self.acceptable_high):
            return 'Unacceptable'
        elif (value < self.ideal_low) | (value > self.ideal_high): 
            return 'Acceptable'
        else:
            assert value >= self.ideal_low 
            assert value <= self.ideal_high
            return 'Ideal'
        
def aggregate_conditions(*conditions):
    '''
    A function to wrap up the decision making process; placeholder until I get more sophisticated logic.
    This will probably involve some kind of scoring based on the counts of ideal / acceptable / unacceptable 
    observations, but I'm not sure about how to weight different conditions or if we want to auto-negate anything
    with an "unacceptable" value (which would be a good use of unacceptable).

    Could use this to set either
    - the color of a constant-height bar in the background; range from some bad value (red/brown) to some good 
      value (probably green but colorblind friendly?)
    - the opacity value of a constant-height green bar; if dark green, get out there!  
    '''
    counts = Counter(conditions)
    if counts['Unacceptable'] != 0:
        return 0 
    else:
        return (2 * counts['Ideal'] + counts['Acceptable']) / sum(counts.values())

    ## old logic:
    # if all([x == 'Ideal' for x in conditions]):
    #     return "Get out there, homie!!!"
    # elif any([x == 'Unacceptable' for x in conditions]):
    #     return "There's a deal-breaker somewhere :/"
    # else:
    #     return "You can probably find something decent to climb!"