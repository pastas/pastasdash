from dash import dcc

from pastasdash.application.components.models import tab_layout as tab_model
from pastasdash.application.components.overview import tab_layout as tab_overview
from pastasdash.application.components.shared import ids


def render():
    """Renders the tab container.

    Returns
    -------
    dcc.Tabs
        A Dash Tabs component containing the overview, model, QC, and QC result tabs.
    """
    return dcc.Tabs(
        id=ids.TAB_CONTAINER,
        value=ids.TAB_OVERVIEW,
        children=[
            tab_overview.render(),
            tab_model.render(),
        ],
    )
