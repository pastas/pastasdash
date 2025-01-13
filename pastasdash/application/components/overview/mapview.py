import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc

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
    selected_data=None,
):
    return dcc.Graph(
        id=ids.OVERVIEW_MAP,
        figure=plot_mapview(
            pstore,
            selected_data=selected_data,
        ),
        style={
            "margin-top": "15",
            "height": "45vh",
        },
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": True,
            "modeBarButtonsToAdd": ["zoom", "zoom2d"],
        },
    )


def plot_mapview(
    pstore,
    selected_data=None,
    update_extent=True,
):
    """Draw ScatterMap.

    Parameters
    ----------
    df : pandas.DataFrame
        data to plot

    Returns
    -------
    dict
        dictionary containing plotly maplayout and mapdata
    """
    oseries = add_latlon_to_dataframe(pstore.oseries.reset_index())
    stresses = add_latlon_to_dataframe(pstore.stresses.reset_index())

    oseries["z"] = oseries.loc[:, ["screen_top", "screen_bot"]].mean(axis=1)
    oseries.sort_values("z", ascending=True, inplace=True)
    msize = 15 + 100 * (oseries["z"].max() - oseries["z"]) / (
        oseries["z"].max() - oseries["z"].min()
    )
    msize.fillna(20, inplace=True)

    if selected_data is not None:
        pts_data = np.nonzero(oseries["name"].isin(selected_data))[0].tolist()
    else:
        pts_data = None

    # oseries data for map
    oseries_data = {
        "lat": oseries.loc[:, "lat"],
        "lon": oseries.loc[:, "lon"],
        "name": "Observation wells",
        "customdata": oseries.loc[:, "z"],
        "type": "scattermap",
        "text": oseries.loc[:, "name"].tolist(),
        "textposition": "top center",
        "textfont": {"size": 12, "color": "black"},
        "mode": "markers+text",
        "marker": go.scattermap.Marker(
            size=msize,
            opacity=0.7,
            sizeref=0.5,
            sizemin=2,
            sizemode="area",
            color=oseries["z"],
            colorscale=px.colors.sequential.Reds,
            reversescale=False,
            showscale=True,
            colorbar={
                "title": "depth<br>(m+ref)",
                "x": 1.0,
                "y": 0.95,
                "len": 0.95,
                "yanchor": "top",
            },
        ),
        "cluster": {"enabled": False},
        "hovertemplate": ("<b>%{text}</b><br>" + "<b>z:</b> NAP%{marker.color:.2f} m"),
        "showlegend": True,
        "legendgroup": "DATA",
        "selectedpoints": pts_data,
        "unselected": {"marker": {"opacity": 0.5}},
        "selected": {"marker": {"opacity": 1.0, "color": "red", "size": 9}},
    }

    # stresses data for map
    kind_dict = {}
    for i, k in enumerate(stresses.kind.unique()):
        kind_dict[k] = px.colors.qualitative.Antique[i]

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

    mapdata = [oseries_data] + stresses_data

    if selected_data is None:
        zoom, center = get_plotting_zoom_level_and_center_coordinates(
            oseries.lon.values, oseries.lat.values
        )
    else:
        sel = oseries.iloc[selected_data]
        zoom, center = get_plotting_zoom_level_and_center_coordinates(
            sel.lon.values, sel.lat.values
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
            "zoom": zoom,
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
        "uirevision": False,
        "modebar": {
            "bgcolor": "rgba(255,255,255,0.9)",
        },
    }

    if update_extent:
        maplayout["uirevision"] = not bool(int(maplayout["uirevision"]))

    return {"data": mapdata, "layout": maplayout}
