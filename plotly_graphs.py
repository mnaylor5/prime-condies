import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

def plot_daily_forecast(daily_df, filter_to_daytime=True):
    """
    The daily_df has a `name` attribute which is more useful than the timestamps

    TODO:
    - color background according to overall conditions (see "Add Lines and Rectangles" on https://plotly.com/python/facet-plots/)
    - summary in hovertext?
    """
    if filter_to_daytime:
        daily_df = daily_df.query("isDaytime")
    melted = daily_df.melt(id_vars = ['area', 'name', 'condition_score'], value_vars=['temperature', 'humidity', 'precipitation'], var_name="condition")

    melted['condition_bucket'] = ['PRIME' if x == 2 else 'Trash :(' if x == 0 else 'Maybe decent' for x in melted['condition_score']]
    melted['condition'] = melted['condition'].str.title()
    fig = px.line(melted, x="name", y="value", color="condition", line_dash="condition", facet_col="area", 
                  facet_col_wrap=2, facet_col_spacing=0.06, hover_name='condition_bucket',
                  markers=True, facet_row_spacing=0.06, height=800, width=900)

    fig.update_layout(title="7-Day Forecast", xaxis_title=None)
    fig.update_yaxes(title=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_legends(title=None)
    return fig

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