import dash_bootstrap_components as dbc
from dash import dcc

from pastasdash.application.cache import TIMEOUT, cache
from pastasdash.application.components.overview import chart, datatable, mapview
from pastasdash.application.components.shared import ids
from pastasdash.application.datasource import PastaStoreInterface
from pastasdash.application.settings import settings
from pastasdash.application.utils import conditional_decorator


def render():
    """Renders a Dash Tab component for the overview tab.

    Returns
    -------
    dcc.Tab
        overview tab
    """
    return dcc.Tab(
        label="Time Series",
        value=ids.TAB_OVERVIEW,
        className="custom-tab",
        selected_className="custom-tab--selected",
    )


@conditional_decorator(cache.memoize, settings["CACHING"], timeout=TIMEOUT)
def render_content(pstore: PastaStoreInterface, selected_data: str):
    """Renders the content for the overview tab.

    Parameters
    ----------
    data : DataInterface
        The data interface object containing the data to be rendered.
    selected_data : str
        The identifier for the selected data to be displayed.

    Returns
    -------
    dbc.Container
        A Dash Bootstrap Component container with the rendered content,
        including a map, table, and chart.
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            mapview.render(pstore, selected_data),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            datatable.render(pstore, selected_data),
                        ],
                        width=6,
                    ),
                ],
                style={"height": "45vh"},
            ),
        ]
        + (
            [dbc.Row(dbc.Col(chart.render_cancel_button()), width="auto")]
            if settings["BACKGROUND_CALLBACKS"]
            else []
        )
        + [
            dbc.Row(
                [
                    chart.render(pstore, selected_data),
                ],
            ),
        ],
        fluid=True,
    )
