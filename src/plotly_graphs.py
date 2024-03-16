import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

score_to_name = {1:"PRIME", 0.75:"Great", 0.5:"Pretty good", 0.25:"Better than the gym", 0:"Trash :(", '':"No data"}

def plot_daily_bar_chart(hourly_df):
    daily_agg = hourly_df\
        .groupby(["area", "forecast_period", "condition_score"], as_index=False)\
        .agg(good_hours = ("condition_score", lambda x : (x > 0).sum()), start_time= ("startTime", "min"))\
        .sort_values(["area", "start_time"])
    
    fig = px.bar(daily_agg, 
                 x="forecast_period", 
                 y="good_hours", 
                 text="good_hours",
                 color="condition_score", 
                 color_continuous_scale="greens",
                 range_color=(0, 1),
                 facet_row="area",
                 facet_row_spacing=0.15, 
                 height=800,
                 barmode="stack")
    
    fig.for_each_annotation(lambda a: a.update(text=f'<em>{a.text.split("=")[1]}<em>', y=a.y + 0.09, x = 0, textangle=0))
    fig.update_xaxes(showticklabels=True, title='')
    fig.update_yaxes(title='')
    fig.add_annotation(x = -0.1, y=0.5, textangle=-90, text="Good Hours", showarrow=False, xref="paper", yref="paper")
    
    fig.update_layout(
        coloraxis_colorbar = dict(
            title=None,
            orientation="h",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            labelalias = score_to_name,
            ticks="outside",
            y=1.0,
            yref="paper"
    ))

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
            labelalias = score_to_name,
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
    fig.update_layout(title=f"Hourly Forecast Values for {df['area'].iloc[0]}", bargap=0.0,
                      legend=dict(orientation='h', y=0.05, yref='container'))
    return fig