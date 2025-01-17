import pandas as pd
from dash import Input, Output, State, dcc
from dash.exceptions import PreventUpdate

from pastasdash.application.components.maps.mapview import (
    get_value_from_pastastore,
    plot_mapview_results,
)
from pastasdash.application.components.shared import ids
from pastasdash.application.utils import derive_input_parameters


def register_maps_callbacks(app, pstore):
    """Register the map callbacks.

    Parameters
    ----------
    app : object
        The application instance to which the callbacks will be registered.
    pstore : object
        The pastastore interface that will be used by the callbacks.
    """

    @app.callback(
        Output(ids.MAP_RESULT_FIGURE, "figure"),
        Output(ids.DOWNLOAD_MAP_DATA_STORE, "data"),
        Output(ids.DOWNLOAD_MAPDATA_BUTTON, "disabled"),
        Output(ids.MAPDATA_CMAP_MIN, "value"),
        Output(ids.MAPDATA_CMAP_MAX, "value"),
        Output(ids.MAPDATA_CMAP_MIN, "step"),
        Output(ids.MAPDATA_CMAP_MAX, "step"),
        Input(ids.MAP_RENDER_BUTTON, "n_clicks"),
        State(ids.MAP_DROPDOWN_SELECTION, "value"),
        State(ids.MAP_COLORMAP_SELECTION, "value"),
        State(ids.REVERSE_COLORMAP_CHECKBOX, "value"),
        State(ids.MAPDATA_CMAP_MIN, "value"),
        State(ids.MAPDATA_CMAP_MAX, "value"),
    )
    def generate_map(n_clicks, value, cmap, reverse, vmin, vmax):
        if n_clicks:
            cmap = cmap + "_r" if reverse else cmap
            # TODO: join on model names instead of oseries
            data = get_value_from_pastastore(pstore, value)
            cmin = data.min().item() if vmin is None else vmin
            cmax = data.max().item() if vmax is None else vmax
            cmin_input, _, stepmin = derive_input_parameters(cmin, precision=2)
            cmax_input, _, stepmax = derive_input_parameters(cmax, precision=2)

            data = data.join(pstore.oseries).reset_index()
            return (
                plot_mapview_results(pstore, data, value, cmap, cmin=cmin, cmax=cmax),
                data.to_dict("records"),
                False,
                cmin_input,
                cmax_input,
                stepmin,
                stepmax,
            )
        else:
            raise PreventUpdate

    @app.callback(
        Output(ids.DOWNLOAD_MAPDATA, "data"),
        Input(ids.DOWNLOAD_MAPDATA_BUTTON, "n_clicks"),
        State(ids.DOWNLOAD_MAP_DATA_STORE, "data"),
        State(ids.MAP_DROPDOWN_SELECTION, "value"),
        prevent_initial_call=True,
    )
    def download_map_data(n_clicks, data, value):
        if n_clicks:
            value_type, v = value.split(":")
            timestr = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestr}_{value_type}_{v}.csv"
            if data is not None:
                return dcc.send_string(pd.DataFrame(data).to_csv, filename=filename)
