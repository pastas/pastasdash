import dash_bootstrap_components as dbc
from dash import dcc, html

from pastasdash.application.components.shared import ids
from pastasdash.application.settings import ASSETS_PATH

# load Modal helper text from MarkDown
with open(ASSETS_PATH / "pastasdash_help.md", "r", encoding="utf-8") as f:
    help_md = dcc.Markdown("".join(f.readlines()), mathjax=True)


def render():
    """Renders a help button and modal for the GW DataLens application.

    This function creates a button that, when clicked, opens a modal containing
    information about the GW DataLens application. The modal includes a header,
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
