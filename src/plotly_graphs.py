import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

score_to_name = {1:"PRIME", 0.75:"Great", 0.5:"Pretty good", 0.25:"Better than the gym", 0:"Trash :(", '':"No data"}

def plot_daily_bar_chart(area_hourly_df, title):
    '''
    Plot daily conditions as a bar chart of decent hours within each 12-hour period. Drops
    any period with 2 or fewer hours present to avoid showing an empty day at the beginning 
    or end of the time range
    '''
    daily_agg = area_hourly_df\
        .groupby(["forecast_period", "condition_score"], as_index=False)\
        .agg(good_hours = ("condition_score", lambda x : (x > 0).sum()), 
             start_time= ("startTime", "min"),
             total_hours = ("startTime", "count"))\
        .query("total_hours >= 2")\
        .sort_values(["start_time"])
    
    fig = px.bar(daily_agg, 
                 x="forecast_period", 
                 y="good_hours", 
                 color="condition_score", 
                 color_continuous_scale="greens",
                 range_color=(0, 1),
                 height=300,
                 title=title,
                 barmode="stack")
    
    grouped = daily_agg.groupby("forecast_period").agg({'good_hours':'sum'})
    fig.add_trace(go.Scatter(
        x=grouped.index, 
        y=grouped['good_hours'],
        text=grouped['good_hours'],
        mode='text',
        textposition='top center',
        showlegend=False
    ))
    
    fig.update_layout(
        yaxis=dict(title="Good Hours", tickvals=[0, 3, 6, 9, 12], range=[0, 13.5]),
        xaxis=dict(title=None),
        coloraxis_colorbar = dict(
            title=None,
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            labelalias = score_to_name,
            ticks="outside",
    ))

    return fig

def plot_hourly_forecast_values(df):
    '''
    Use a pre-filtered (to location and time frame) dataframe to plot raw hourly forecasts along with
    the composite condition score as the background color
    '''
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x = df['startTime'], 
               y=df['startTime'].apply(lambda x: 100),
               marker_color=df['condition_score'], 
               marker_colorscale="greens", 
               marker_cmax=0.0,
               marker_cmin=1.0,
               opacity=0.5, 
               name="Condition Quality"
    ))
    fig.add_trace(go.Scatter(x = df['startTime'], y=df['temperature'], name="Temperature"))
    fig.add_trace(go.Scatter(x = df['startTime'], y=df['humidity'], name="Humidity"))
    fig.add_trace(go.Scatter(x = df['startTime'], y=df['precipitation'], name="Precipitation %"))
    fig.add_trace(go.Scatter(x = df['startTime'], y=df['dewpoint_f'], name="Dewpoint", marker_color="black"))
    fig.update_layout(title=f"Hourly Forecast Values for {df['area'].iloc[0]}", bargap=0.0,
                      legend=dict(orientation='h', y=0.05, yref='container'))
    return fig