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
    stresses = add_latlon_to_dataframe(pstore.stresses)

    msize = 15 + 100 * (oseries["z"].max() - oseries["z"]) / (
        oseries["z"].max() - oseries["z"].min()
    )
    msize.fillna(20, inplace=True)

    if selected_data is not None:
        if isinstance(selected_data[0], int):
            pts_data = selected_data
        elif isinstance(selected_data[0], str):
            pts_data = oseries.loc[selected_data, "id"].tolist()
        else:
            raise ValueError("selected_data should be a list of integers or strings.")

        # # attempt getting selected oseries on top, for better visibility in plot
        # # highlighting
        # reordered_idx = [i for i in oseries.index if i not in pts_data] + pts_data
        # oseries = oseries.loc[reordered_idx]

        selectedData = {
            "points": [
                {
                    "curveNumber": 0,
                    "pointNumber": idx,
                    "pointIndex": idx,
                    "lon": oseries.reset_index().set_index("id").loc[idx, "lon"],
                    "lat": oseries.reset_index().set_index("id").loc[idx, "lat"],
                    "text": oseries.reset_index().set_index("id").loc[idx, "name"],
                }
                for idx in pts_data
            ]
        }
    else:
        pts_data = None
        selectedData = None

    # oseries data for map
    oseries_data = {
        "lat": oseries.loc[:, "lat"],
        "lon": oseries.loc[:, "lon"],
        "name": "Observation wells",
        "customdata": oseries.loc[:, "z"],
        "type": "scattermap",
        "text": oseries.index.tolist(),
        "textposition": "top center",
        "textfont": {"size": 12, "color": "black"},
        "mode": "markers",
        "marker": go.scattermap.Marker(
            size=msize,
            opacity=0.7,
            sizeref=0.5,
            sizemin=2,
            sizemode="area",
            color=oseries["z"],
            colorscale=px.colors.sequential.Tealgrn,
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
        "unselected": {"marker": {"opacity": 0.1}},
        "selected": {"marker": {"opacity": 1.0, "color": "black", "size": 9}},
        "selectedData": selectedData,
    }

    # stresses data for map
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
                "text": sdf.index.tolist(),
                "textposition": "top center",
                "textfont": {
                    "size": 11,
                    "color": "darkslategray",
                },
                "customdata": sdf["kind"],
                "mode": "markers",
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
                "unselected": {"marker": {"opacity": 0.7}},
                "selected": {"marker": {"opacity": 1.0}},
            }
        )

    mapdata = [oseries_data] + stresses_data

    if selected_data is None:
        zoom, center = get_plotting_zoom_level_and_center_coordinates(
            oseries.lon.values, oseries.lat.values
        )
        zoom = zoom + 3  # NOTE: manual correction to show all obs
    else:
        sel = oseries.reset_index().set_index("id").loc[pts_data]
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
        },
        "legend": {"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top"},
        # "legend": {"x": 0.99, "y": 0.99, "xanchor": "right", "yanchor": "top"},
        "uirevision": False,
        "modebar": {
            "bgcolor": "rgba(255,255,255,0.9)",
        },
        "selectdirection": "d",
    }

    if update_extent:
        maplayout["uirevision"] = not bool(int(maplayout["uirevision"]))

    return {"data": mapdata, "layout": maplayout}
