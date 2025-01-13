from dash import dcc, html

from pastasdash.application.components.shared import ids


def render(pstore, selected_data):
    """Renders a dropdown component for selecting a time series.

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
    locs = pstore.oseries_names

    options = [{"label": i, "value": i} for i in locs]

    if selected_data is not None and len(selected_data) == 1:
        value = selected_data[0]
    else:
        value = None

    return html.Div(
        [
            dcc.Dropdown(
                id=ids.MODEL_DROPDOWN_SELECTION,
                clearable=True,
                placeholder="Select a location",
                value=value,
                multi=False,
                searchable=True,
                disabled=False,
                options=options,
            )
        ]
    )
