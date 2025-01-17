import pastas as ps
import plotly.express as px
from dash import dcc, html

from pastasdash.application.components.shared import ids
from pastasdash.application.components.shared.styling import get_colormap_figures


def render_value_dropdown(pstore):
    """Renders a dropdown component for selecting a parameter or statistic.

    Parameters
    ----------
    data : object
        An object that contains a database connection with methods to list
        locations and access location data.
    selected_data : list or None
        A list containing the currently selected location(s). If None or the list
        is empty, no location is pre-selected.

    Returns
    -------
    html.Div
        A Dash HTML Div component containing a Dropdown for selecting a location.
    """
    options = []

    for i in pstore.unique_parameters:
        options.append(
            {
                "label": html.Span(f"Parameter: {i}", style={"color": "black"}),
                "value": f"parameter:{i}",
            }
        )

    metrics = ps.modelstats.Statistics.ops
    for i in metrics:
        options.append(
            {
                "label": html.Span(f"Metric: {i}", style={"color": "darkgreen"}),
                "value": f"metric:{i}",
            }
        )

    signatures = ps.stats.signatures.__all__.copy()
    for i in signatures:
        options.append(
            {
                "label": html.Span(f"Signature: {i}", style={"color": "darkred"}),
                "value": f"signature:{i}",
            }
        )

    return html.Div(
        [
            dcc.Dropdown(
                id=ids.MAP_DROPDOWN_SELECTION,
                clearable=True,
                placeholder="Select value to show on map",
                value="parameter:recharge_A",
                searchable=True,
                disabled=False,
                options=options,
                style={"margin-top": 5},
            )
        ]
    )


def render_colormap_dropdown():
    options = (
        [
            {"label": fig, "value": name}
            for name, fig in get_colormap_figures(px.colors.sequential).items()
        ]
        + [
            {"label": fig, "value": name}
            for name, fig in get_colormap_figures(px.colors.diverging).items()
        ]
        + [
            {"label": fig, "value": name}
            for name, fig in get_colormap_figures(px.colors.cyclical).items()
        ]
    )

    return html.Div(
        [
            dcc.Dropdown(
                id=ids.MAP_COLORMAP_SELECTION,
                clearable=True,
                placeholder="Select a colormap",
                value="Turbo",
                searchable=True,
                disabled=False,
                options=options,
                style={"margin-top": 5},
            )
        ]
    )
