import plotly.express as px 
import plotly.graph_objects as go

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