import functools

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html

from pastasdash.application.cache import TIMEOUT, cache
from pastasdash.application.components.shared import ids
from pastasdash.application.datasource import PastaStoreInterface
from pastasdash.application.settings import settings
from pastasdash.application.utils import (
    add_latlon_to_dataframe,
    conditional_decorator,
    get_plotting_zoom_level_and_center_coordinates,
)


@conditional_decorator(cache.memoize, settings["CACHING"], timeout=TIMEOUT)
def render(
    pstore: PastaStoreInterface,
    value=None,
):
    return html.Div(
        id="mapview-div",
        children=dcc.Loading(
            id=ids.LOADING_SERIES_CHART,
            type="dot",
            style={"position": "absolute", "align-self": "center"},
            parent_className="loading-wrapper",
            children=[
                dcc.Graph(
                    id=ids.MAP_RESULT_FIGURE,
                    figure=plot_mapview_results(pstore, None, value, cmap="Turbo_r"),
                    style={
                        "margin-top": "15",
                        "height": "75vh",
                    },
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "scrollZoom": True,
                        "modeBarButtonsToAdd": ["zoom", "zoom2d"],
                    },
                )
            ],
            delay_show=500,
        ),
    )


@functools.lru_cache
def get_value_from_pastastore(pstore, value):
    value_type, v = value.split(":")
    if value_type.lower() == "parameter":
        data = pstore.get_parameters([v], progressbar=True)
    elif value_type.lower() == "metric":
        data = pstore.get_statistics(
            [v], parallel=settings["PARALLEL"], progressbar=True
        )
    elif value_type.lower() == "signature":
        data = pstore.get_signatures([v], progressbar=True)
    else:
        raise ValueError(f"Unknown value: {value_type}: {v}")
    data.index.name = "name"
    if isinstance(data, pd.Series):
        return data.to_frame()
    else:
        return data


def plot_mapview_results(pstore, data, value: str, cmap: str, cmin=None, cmax=None):
    if pstore.empty:
        maplayout = {
            "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
            "font": {"color": "#000000", "size": 11},
            "paper_bgcolor": "white",
            "clickmode": "event+select",
            "map": {
                "bearing": 0,
                "center": {"lon": 5.104480, "lat": 52.092876},
                "pitch": 0,
                "zoom": 5.5,
                "style": "outdoors",
            },
            "legend": {"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top"},
            "uirevision": False,
            "modebar": {
                "bgcolor": "rgba(255,255,255,0.9)",
            },
            "selectdirection": "d",
        }
        return {"data": [{"type": "scattermap"}], "layout": maplayout}

    oseries = add_latlon_to_dataframe(pstore.oseries)

    zoom, center = get_plotting_zoom_level_and_center_coordinates(
        oseries.lon.values, oseries.lat.values
    )

    maplayout = {
        # top, bottom, left and right margins
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
        "font": {"color": "#000000", "size": 11},
        "paper_bgcolor": "white",
        "clickmode": "event+select",
        "map": {
            "bearing": 0,
            # where we want the map to be centered
            "center": center,
            # we want the map to be "parallel" to our screen, with no angle
            "pitch": 0,
            # default level of zoom
            "zoom": zoom + 4,
            # default map style (some options listed, not all support labels)
            "style": "outdoors",
            # public styles
            # style="carto-positron",
            # style="open-street-map",
            # style="stamen-terrain",
            # style="basic",
            # style="streets",
            # style="light",
            # style="dark",
            # style="satellite",
            # style="satellite-streets"
        },
        "legend": {"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top"},
        # "legend": {"x": 0.99, "y": 0.99, "xanchor": "right", "yanchor": "top"},
        "uirevision": True,
        "modebar": {
            "bgcolor": "rgba(255,255,255,0.9)",
        },
    }

    # stresses data for map
    stresses = add_latlon_to_dataframe(pstore.stresses.reset_index())
    kind_dict = {}
    for i, k in enumerate(stresses.kind.unique()):
        kind_dict[k] = px.colors.qualitative.G10[i]

    stresses_data = []
    for kind, sdf in stresses.groupby("kind"):
        stresses_data.append(
            {
                "lat": sdf["lat"],
                "lon": sdf["lon"],
                "name": kind,
                "type": "scattermap",
                "text": sdf["name"].tolist(),
                "textposition": "top center",
                "textfont": {
                    "size": 11,
                    "color": "darkslategray",
                },
                "customdata": sdf["kind"],
                "mode": "markers+text",
                "marker": go.scattermap.Marker(
                    symbol="circle",
                    size=10,
                    opacity=1.0,
                    color=kind_dict[kind],
                ),
                "hovertemplate": (
                    "<b>%{text}</b><br>"
                    + "<b>kind:</b> %{customdata}"
                    + "<extra></extra> "
                ),
                "showlegend": True,
                "unselected": {"marker": {"opacity": 0.9}},
                "selected": {"marker": {"opacity": 1.0}},
            }
        )

    if value is None:
        return {"data": stresses_data, "layout": maplayout}
    else:
        value_type, v = value.split(":")
    data = get_value_from_pastastore(pstore, value)

    # TODO: add model oseries name as column and join on that
    mdata = data.join(oseries).reset_index()

    mdata["z"] = mdata.loc[:, ["screen_top", "screen_bot"]].mean(axis=1)
    mdata.sort_values("z", ascending=True, inplace=True)
    msize = 15 + 100 * (mdata["z"].max() - mdata["z"]) / (
        mdata["z"].max() - mdata["z"].min()
    )
    msize.fillna(20, inplace=True)
    mdata.sort_values("z", ascending=False, inplace=True)

    # data for map
    traces = []
    mask = mdata[v].isna()
    if not mask.all():
        map_data = {
            "lat": mdata.loc[~mask, "lat"],
            "lon": mdata.loc[~mask, "lon"],
            "name": "Models",
            "customdata": mdata.loc[~mask, "z"],
            "type": "scattermap",
            "text": mdata.loc[~mask, "name"].tolist(),
            "textposition": "top center",
            "textfont": {"size": 12, "color": "black"},
            "mode": "markers",
            "marker": go.scattermap.Marker(
                size=msize,
                opacity=0.7,
                sizeref=0.5,
                sizemin=2,
                sizemode="area",
                color=mdata.loc[~mask, v],
                colorscale=cmap.lower(),
                cmin=cmin,
                cmax=cmax,
                reversescale=False,
                showscale=True,
                colorbar={
                    "title": f"{value_type}:<br>{v}",
                    "x": 1.0,
                    "y": 0.95,
                    "len": 0.95,
                    "yanchor": "top",
                },
            ),
            "cluster": {"enabled": False},
            "hovertemplate": (
                "<b>%{text}</b><br>"
                + "<b>"
                + v
                + ":</b> %{marker.color:.2f}<br>"
                + "<b>z:</b> NAP%{customdata:.2f} m"
                + "<extra></extra> "
            ),
            "showlegend": True,
            "legendgroup": "DATA",
            # "selectedpoints": pts_data,
            "unselected": {"marker": {"opacity": 1.0}},
            # "selected": {"marker": {"opacity": 1.0, "color": "red", "size": 9}},
        }
        traces.append(map_data)

    if mask.any():
        map_nodata = {
            "lat": mdata.loc[mask, "lat"],
            "lon": mdata.loc[mask, "lon"],
            "name": "Models",
            "customdata": mdata.loc[mask, "z"],
            "type": "scattermap",
            "text": mdata.loc[mask, "name"].tolist(),
            "textposition": "top center",
            "textfont": {"size": 12, "color": "black"},
            "mode": "markers",
            "marker": go.scattermap.Marker(
                size=msize,
                opacity=0.7,
                sizeref=0.5,
                sizemin=2,
                sizemode="area",
                color="gray",
            ),
            "cluster": {"enabled": False},
            "hovertemplate": ("<b>%{text}</b><br>" + "<b>{value}:</b>% No data"),
            "showlegend": True,
            "legendgroup": "NODATA",
            "unselected": {"marker": {"opacity": 1.0}},
            # "selected": {"marker": {"opacity": 1.0, "color": "red", "size": 9}},
        }
        traces.append(map_nodata)

    return {"data": traces + stresses_data, "layout": maplayout}
