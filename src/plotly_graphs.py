import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

score_to_name = {1:"PRIME", 0.75:"Great", 0.5:"Pretty good", 0.25:"Better than the gym", 0:"Trash :(", '':"No data"}

def plot_daily_heatmap(daily_df, filter_to_daytime=True):
    '''
    Use the wide/tidy `daily_df` to plot a heatmap whose rows are areas and columns
    are forecast entries
    '''
    df = daily_df.query("isDaytime") if filter_to_daytime else daily_df 

    names_in_order = df['name'].unique()
    daily_heatmap_df = df.set_index('area')\
        [['name', 'condition_score']]\
        .pivot(columns='name', values='condition_score')[names_in_order]
    
    daily_heatmap_df['sum'] = daily_heatmap_df.sum(axis=1)
    daily_heatmap_df = daily_heatmap_df.sort_values("sum")[names_in_order]
    heatmap_data = daily_heatmap_df.fillna('').values
    heatmap_text = np.vectorize(score_to_name.__getitem__)(heatmap_data)
    
    fig = go.Figure(data = go.Heatmap(
        z = heatmap_data,
        text = heatmap_text,
        x = names_in_order,
        y = daily_heatmap_df.index,
        hovertemplate="%{x} at %{y}:<br>%{text}",
        zmin=0,
        zmax=1,
        xgap=0.2,
        ygap=0.2,
        colorscale="greens", 
        colorbar = dict(
            tickmode="array",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext = [score_to_name[x] for x in [0, 0.25, 0.5, 0.75, 1]],
            ticks="outside"
        )
    ))
    fig.update_layout(title="High Level Condition Outlook (Best Options First)", template="plotly_white")
    return fig

def plot_hourly_heatmap(hourly_df, periods=48):
    '''
    Use the wide/tidy `daily_df` to plot a heatmap whose rows are areas and columns
    are forecast entries
    '''

    min_period = hourly_df['number'].min()
    max_period = min_period + periods

    hourly_heatmap_df = hourly_df.set_index('area')\
        .query(f"number < {max_period}")\
        [['startTime', 'condition_score']]\
        .pivot(columns='startTime', values='condition_score')
    
    hourly_heatmap_df['sum'] = hourly_heatmap_df.sum(axis=1)
    hourly_heatmap_df = hourly_heatmap_df.sort_values("sum").drop(columns='sum')
    heatmap_data = hourly_heatmap_df.fillna('').values
    heatmap_text = np.vectorize(score_to_name.__getitem__)(heatmap_data)
    
    fig = go.Figure(data = go.Heatmap(
        z = heatmap_data,
        text = heatmap_text,
        x = hourly_heatmap_df.columns,
        y = hourly_heatmap_df.index,
        hovertemplate="%{x} at %{y}:<br>%{text}",
        zmin=0,
        zmax=1,
        xgap=0.2,
        ygap=0.2,
        name="",
        colorscale="greens", 
        colorbar = dict(
            tickmode="array",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext = [score_to_name[x] for x in [0, 0.25, 0.5, 0.75, 1]],
            ticks="outside"
        )
    ))
    fig.update_layout(title="Hourly Condition Outlook (Best Options First)", template="plotly_white")
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
    fig.update_layout(title=f"Hourly Forecast Values for {df['area'].iloc[0]}", bargap=0.0)
    return fig