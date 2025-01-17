from typing import List

import dash_bootstrap_components as dbc
from dash import dcc

from pastasdash.application.components.models import (
    button,
    datepicker,
    dropdown,
    plots,
)
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
        label="Model Results",
        value=ids.TAB_MODEL,
        className="custom-tab",
        selected_className="custom-tab--selected",
    )


def render_content(pstore: PastaStoreInterface, selected_data: List):
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
                    dbc.Col([dropdown.render(pstore, selected_data)], width=4),
                    dbc.Col(
                        [datepicker.render_datepicker_tmin(pstore, selected_data)],
                        width="auto",
                    ),
                    dbc.Col(
                        [datepicker.render_datepicker_tmax(pstore, selected_data)],
                        width="auto",
                    ),
                    dbc.Col([button.render_solve_button()], width="auto"),
                    dbc.Col([button.render_save_button()], width="auto"),
                ],
            ),
            dbc.Row(
                [
                    # Column 1: Model results plot
                    dbc.Col(
                        children=[
                            plots.render_results(),
                        ],
                        width=6,
                    ),
                    # Column 2: Model diagnostics plot
                    dbc.Col(
                        children=[
                            plots.render_diagnostics(),
                        ],
                        width=6,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
