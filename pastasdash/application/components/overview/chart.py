import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import __version__ as DASH_VERSION
from dash import dcc, html
from packaging.version import parse as parse_version

from pastasdash.application.components.shared import ids


def render_cancel_button():
    """Renders a cancel button component.

    Returns
    -------
    html.Div
        A Div containing a disabled cancel button.
    """
    return html.Div(
        children=[
            dbc.Button(
                html.Span(
                    [
                        html.I(className="fa-regular fa-circle-stop"),
                        " Cancel",
                    ],
                    id="span-cancel-button",
                    n_clicks=0,
                ),
                style={
                    "margin-top": 10,
                    "margin-bottom": 10,
                },
                disabled=True,
                id=ids.OVERVIEW_CANCEL_BUTTON,
            ),
        ]
    )


def render(pstore, selected_data):
    kwargs = (
        {"delay_show": 500}
        if parse_version(DASH_VERSION) >= parse_version("2.17.0")
        else {}
    )
    return html.Div(
        id="series-chart-div",
        children=[
            dcc.Loading(
                id=ids.LOADING_SERIES_CHART,
                type="dot",
                style={"position": "absolute", "align-self": "center"},
                parent_className="loading-wrapper",
                children=[
                    dcc.Graph(
                        figure=plot_timeseries(pstore, selected_data),
                        id=ids.SERIES_CHART,
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                        },
                        style={
                            "height": "40vh",
                        },
                    ),
                ],
                **kwargs,
            ),
        ],
        style={
            "position": "relative",
            "justify-content": "center",
            "margin-bottom": 10,
        },
    )


def plot_timeseries(pstore, names):
    """Plots observation data for given names.

    Parameters
    ----------
    pstore : PastaStoreInterface
        pastastore interface
    names : list of str
        List of strings of observation timeseries

    Returns
    -------
    dict
        A dictionary containing plot data and layout configuration for the observations.

    Notes
    -----
    - If `names` is None, returns a layout with a title indicating no plot.
    - If a name is not found in the database, it is skipped.
    - For a single name, plots the timeseries data with different qualifiers and manual
      observations.
    - For multiple names, plots the timeseries data with markers and lines.
    """
    if names is None:
        return {"layout": {"title": "No time series selected"}}

    no_data = []
    traces = []
    for name in names:
        ts = pstore.get_oseries(name)

        # no obs
        if ts.empty:
            no_data.append(True)
            continue

        if len(names) == 1:
            no_data.append(False)
            trace_i = go.Scattergl(
                x=ts.index,
                y=ts.values,
                mode="markers+lines",
                line={"width": 1, "color": "gray"},
                marker={"size": 3},
                name=name,
                legendgroup=name,
                showlegend=True,
            )
            traces.append(trace_i)
        else:
            no_data.append(False)
            trace_i = go.Scattergl(
                x=ts.index,
                y=ts.values,
                mode="markers+lines",
                line={"width": 1},
                marker={"size": 3},
                name=name,
                legendgroup=name,
                showlegend=True,
            )
            traces.append(trace_i)

    layout = {
        "yaxis": {"title": "(m NAP)"},
        "legend": {
            "traceorder": "reversed+grouped",
            "orientation": "h",
            "xanchor": "left",
            "yanchor": "bottom",
            "x": 0.0,
            "y": 1.02,
        },
        "dragmode": "pan",
        "margin-top": 0,
    }
    if all(no_data):
        return None
    else:
        return {"data": traces, "layout": layout}
