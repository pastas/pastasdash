import dash_bootstrap_components as dbc
from dash import html

from pastasdash.application.components.shared import ids


def render_select_all_in_table_button():
    """Renders a button for selecting all rows in table.

    Returns
    -------
    html.Div
        A Dash HTML Div containing the button.
    """
    return html.Div(
        dbc.Button(
            html.Span(
                [
                    html.I(className="fa-solid fa-check-double"),
                    " " + "Select All",
                ],
                id="span-select-all",
                n_clicks=0,
            ),
            style={
                "margin-top": 10,
                "margin-bottom": 10,
            },
            disabled=False,
            id=ids.COMPARE_TABLE_SELECT_ALL_BUTTON,
        ),
    )


def render_deselect_all_in_table_button():
    """Renders a button for selecting all rows in table.

    Returns
    -------
    html.Div
        A Dash HTML Div containing the button.
    """
    return html.Div(
        dbc.Button(
            html.Span(
                [
                    html.I(className="fa-solid fa-ban"),
                    " " + "Clear selection",
                ],
                id="span-select-all",
                n_clicks=0,
            ),
            style={
                "margin-top": 10,
                "margin-bottom": 10,
            },
            disabled=False,
            id=ids.COMPARE_TABLE_DESELECT_ALL_BUTTON,
        ),
    )
