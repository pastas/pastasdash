from dash import Dash, dcc, html

from pastasdash.application.components import buttons
from pastasdash.application.components.shared import ids, tabcontainer
from pastasdash.application.datasource import PastaStoreInterface


def create_layout(app: Dash, pstore: PastaStoreInterface) -> html.Div:
    """Create app layout.

    Parameters
    ----------
    app : Dash
        dash app object
    data : DataInterface
        data class

    Returns
    -------
    html.Div
        html containing app layout.
    """
    return html.Div(
        id="main",
        children=[
            # stores for tab interactivity
            dcc.Store(id=ids.SELECTED_OSERIES_STORE),
            dcc.Store(id=ids.PASTAS_MODEL_STORE),
            dcc.Store(id=ids.DOWNLOAD_MAP_DATA_STORE),
            dcc.Store(id=ids.PASTASTORE_CONFIG_FILE_STORE),
            # avoiding duplicate callback stores
            dcc.Store(id=ids.OVERVIEW_TABLE_SELECTION_1),
            dcc.Store(id=ids.OVERVIEW_TABLE_SELECTION_2),
            # alert containers
            dcc.Store(id=ids.ALERT_TAB_RENDER),
            dcc.Store(id=ids.ALERT_TIME_SERIES_CHART),
            dcc.Store(id=ids.ALERT_PLOT_MODEL_RESULTS),
            dcc.Store(id=ids.ALERT_SOLVE_MODEL),
            dcc.Store(id=ids.ALERT_SAVE_MODEL),
            # header + tabs
            html.Div(
                id="header",
                children=[
                    html.H1(app.title, id="app_title"),
                    html.Div(id=ids.ALERT_DIV),
                    buttons.render_load_pastastore_button(),
                    buttons.render_help_button_modal(),
                ],
            ),
            tabcontainer.render(),
            html.Div(id=ids.TAB_CONTENT),
        ],
    )
