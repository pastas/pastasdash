import dash_bootstrap_components as dbc
from dash import dcc

from pastasdash.application.cache import TIMEOUT, cache
from pastasdash.application.components.compare import (
    buttons,
    chart,
    datatable,
    dropdown,
    mapview,
)
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
        label="Compare models",
        value=ids.TAB_COMPARE,
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
                            datatable.render_metadata_table(pstore, selected_data),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [buttons.render_select_all_in_table_button()],
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        [buttons.render_deselect_all_in_table_button()],
                                        width="auto",
                                    ),
                                ],
                            ),
                        ],
                        class_name="col-right-border",
                        width=4,
                        style={"right-border": "1px solid #d3d3d3"},
                    ),
                    dbc.Col(
                        [
                            dropdown.render(pstore, selected_data),
                            chart.render(),
                            datatable.render_parameters_table(),
                            datatable.render_modelchecks_table(),
                        ],
                    ),
                ],
            ),
        ],
        fluid=True,
    )
