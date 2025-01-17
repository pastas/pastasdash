from dash import dcc

from pastasdash.application.cache import TIMEOUT, cache
from pastasdash.application.components.overview.mapview import plot_mapview
from pastasdash.application.components.shared import ids
from pastasdash.application.datasource import PastaStoreInterface
from pastasdash.application.settings import settings
from pastasdash.application.utils import conditional_decorator


@conditional_decorator(cache.memoize, settings["CACHING"], timeout=TIMEOUT)
def render(pstore: PastaStoreInterface, selected_data=None):
    fig = plot_mapview(pstore, selected_data=selected_data)
    return dcc.Graph(
        id=ids.COMPARE_MAP,
        figure=fig,
        style={
            "margin-top": "15",
            "height": "40vh",
            "background-color": "lightgray",
        },
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": True,
            "modeBarButtonsToAdd": ["zoom", "zoom2d"],
        },
    )
