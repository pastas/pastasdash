from dash import dcc, html
from dash_bootstrap_components import Button, Tooltip

from pastasdash.application.components.shared import ids


def render_map_button():
    """Renders a button for generating time series models.

    Returns
    -------
    html.Div
        A Div containing the generate model button.
    """
    return html.Div(
        [
            Button(
                html.Span(
                    [
                        html.I(className="fa-regular fa-map"),
                        " " + "Generate map",
                    ],
                    id="span-render-map",
                    n_clicks=0,
                ),
                style={
                    "margin-top": 5,
                    "margin-bottom": 5,
                },
                disabled=False,
                id=ids.MAP_RENDER_BUTTON,
            ),
            Tooltip(
                children=[
                    html.P(
                        (
                            "This can take a while depending "
                            "on the selected map parameter. "
                            "The result is cached so subsequent calls to "
                            "'Generate map' will be faster."
                        ),
                        style={"margin-bottom": 0},
                    ),
                ],
                target=ids.MAP_RENDER_BUTTON,
                placement="right",
            ),
        ]
    )


def render_download_mapdata_as_csv_button():
    """Renders a button for generating time series models.

    Returns
    -------
    html.Div
        A Div containing the generate model button.
    """
    return html.Div(
        [
            Button(
                html.Span(
                    [
                        html.I(className="fa-solid fa-file-csv"),
                        " " + "Download data",
                    ],
                    id="span-render-download-csv",
                    n_clicks=0,
                ),
                style={
                    "margin-top": 5,
                    "margin-bottom": 5,
                },
                disabled=True,
                id=ids.DOWNLOAD_MAPDATA_BUTTON,
            ),
            Tooltip(
                children=[
                    html.P(
                        ("Download the data shown on the map as a CSV file."),
                        style={"margin-bottom": 0},
                    ),
                ],
                target=ids.DOWNLOAD_MAPDATA_BUTTON,
                placement="right",
            ),
            dcc.Download(id=ids.DOWNLOAD_MAPDATA),
        ]
    )
