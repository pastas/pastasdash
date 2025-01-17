import dash_bootstrap_components as dbc
from dash import dcc

from pastasdash.application.components.maps import button, dropdown, mapview
from pastasdash.application.components.shared import ids
from pastasdash.application.datasource import PastaStoreInterface


def render():
    """Renders the Model Tab.

    Returns
    -------
    dcc.Tab
        The model tab
    """
    return dcc.Tab(
        label="Results Maps",
        value=ids.TAB_MAPS,
        className="custom-tab",
        selected_className="custom-tab--selected",
    )


def render_reverse_checkbox():
    """Renders a checkbox component for running error detection on subset of obs.

    Returns
    -------
    dbc.Checkbox
        A checkbox allowing the user to select whether to run error detection
        only on unvalidated observations, or on all observations.
    """
    return dbc.Checkbox(
        id=ids.REVERSE_COLORMAP_CHECKBOX,
        label="Reverse colormap",
        value=False,
        style={"margin-top": 10},
    )


def render_content(pstore: PastaStoreInterface):
    """Renders the content for the model tab.

    Parameters
    ----------
    data : DataInterface
        The data interface containing the necessary data for rendering.
    selected_data : List
        A list of selected data items.

    Returns
    -------
    dbc.Container
        A Dash Bootstrap Container with the rendered content.
    """
    return dbc.Container(
        [
            dbc.Row(
                children=[
                    dbc.Col([dropdown.render_value_dropdown(pstore)], width=2),
                    dbc.Col([dropdown.render_colormap_dropdown()], width=2),
                    dbc.Col([render_reverse_checkbox()], width="auto"),
                    dbc.Col(
                        [dbc.Label("Min:", style={"margin-top": 10})], width="auto"
                    ),
                    dbc.Col(
                        [
                            dbc.Input(
                                id=ids.MAPDATA_CMAP_MIN,
                                type="number",
                                inputmode="numeric",
                                size="sm",
                                style={"margin-top": 7.5, "width": 100},
                                placeholder="-",
                            ),
                            dbc.Tooltip(
                                "Colormap min, leave empty for automatic scaling.",
                                target=ids.MAPDATA_CMAP_MIN,
                                placement="right",
                            ),
                        ],
                        style={"padding-left": 0},
                        width="auto",
                    ),
                    dbc.Col(
                        [dbc.Label("Max:", style={"margin-top": 10})],
                        style={"padding-right": 5},
                        width="auto",
                    ),
                    dbc.Col(
                        [
                            dbc.Input(
                                id=ids.MAPDATA_CMAP_MAX,
                                type="number",
                                inputmode="numeric",
                                size="sm",
                                style={"margin-top": 7.5, "width": 100},
                                placeholder="-",
                            ),
                            dbc.Tooltip(
                                "Colormap max, leave empty for automatic scaling.",
                                target=ids.MAPDATA_CMAP_MAX,
                                placement="right",
                            ),
                        ],
                        style={"padding-left": 0},
                        width="auto",
                    ),
                    dbc.Col([button.render_map_button()], width="auto"),
                    dbc.Col(
                        [button.render_download_mapdata_as_csv_button()], width="auto"
                    ),
                ]
            ),
            dbc.Row(
                children=[dbc.Col(mapview.render(pstore), width=12)],
                # style={"height": "75vh"},
            ),
        ],
        fluid=True,
    )
