import dash_bootstrap_components as dbc
from dash import dcc, html

from pastasdash.application.components.shared import ids
from pastasdash.application.settings import ASSETS_PATH

# load Modal helper text from MarkDown
with open(ASSETS_PATH / "pastasdash_help.md", "r", encoding="utf-8") as f:
    help_md = dcc.Markdown("".join(f.readlines()), mathjax=True)


def render_help_button_modal():
    """Renders a help button and modal for the PastasDash application.

    This function creates a button that, when clicked, opens a modal containing
    information about the PastasDash application. The modal includes a header,
    body with help content, and a footer with developer credits and a close button.

    Returns
    -------
    dash.html.Div
        A Dash HTML Div component containing the help button and modal.
    """
    return html.Div(
        [
            dbc.Button(
                html.Span(
                    [html.I(className="fa-solid fa-circle-info"), " Help"],
                    id="span-open-help",
                    n_clicks=0,
                ),
                id=ids.HELP_BUTTON_OPEN,
                class_name="ms-auto",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            html.H3(
                                "About PastasDash",
                                id=ids.HELP_TITLE,
                            ),
                        ),
                    ),
                    dbc.ModalBody(help_md),
                    dbc.ModalFooter(
                        [
                            html.I("Developed by D.A. Brakenhoff" ", Artesia, 2024"),
                            dbc.Button(
                                "Close",
                                id=ids.HELP_BUTTON_CLOSE,
                                className="ms-auto",
                                n_clicks=0,
                            ),
                        ]
                    ),
                ],
                id=ids.HELP_MODAL,
                is_open=False,
                scrollable=True,
                size="xl",
            ),
        ]
    )


def render_load_pastastore_button():
    """Renders a button for loading a PastasStore from a file.

    Returns
    -------
    dash.html.Div
        A Dash HTML Div component containing the load PastasStore button.
    """
    return html.Div(
        id="div-load-pastastore-button",
        className="load-button-pastastore-div",
        children=[
            dcc.Upload(
                id=ids.LOAD_PASTASTORE_BUTTON,
                accept=".pastastore,.zip",
                children=[
                    html.A(
                        html.Span(
                            [
                                html.I(className="fa-solid fa-file-import"),
                                "  Load PastaStore ",
                            ],
                            style={
                                "color": "white",
                            },
                        )
                    )
                ],
                style={
                    "width": "150px",
                    "height": "37.5px",
                    "lineHeight": "35px",
                    "borderWidth": "1px",
                    "borderStyle": "solid",
                    "borderRadius": "5px",
                    "backgroundClip": "border-box",
                    "backgroundColor": "#006f92",
                    "textAlign": "center",
                    "cursor": "pointer",
                },
            ),
            dbc.Tooltip(
                "Load a PastasStore from a .pastastore or .zip file",
                target=ids.LOAD_PASTASTORE_BUTTON,
                style={"margin-bottom": 0},
                placement="left",
            ),
        ],
        style={
            "display": "inline-block",
            "margin-top": 10,
            "margin-bottom": 10,
            "margin-right": 5,
            "margin-left": "auto",
            "verticalAlign": "middle",
        },
    )
