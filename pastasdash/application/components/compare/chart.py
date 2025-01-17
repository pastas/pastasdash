import pastas as ps
import plotly.graph_objs as go
from dash import dcc, html

from pastasdash.application.components.shared import ids


def render():
    return html.Div(
        children=[
            dcc.Loading(
                id="loading-compare_models-plot",
                delay_show=250,
                type="circle",
                children=[
                    dcc.Graph(
                        id=ids.COMPARE_MODELS_CHART,
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                        },
                        style={
                            "height": "36.75vh",
                            "margin-bottom": 0,
                        },
                    )
                ],
            )
        ]
    )


def plot_model_comparison(mllist, tmin=None, tmax=None):
    """Plotly version of pastas.Model.plot().

    Parameters
    ----------
    mllist : list of pastas.Model
        list of models to plot simulation for
    tmin : pd.Timestamp, optional
        start time for model simulation, by default None
    tmax : pd.Timestamp, optional
        end time for model simulation, by default None

    Returns
    -------
    dict
        dictionary containing plotly Scatter data and layout
    """
    traces = []

    if isinstance(mllist, ps.Model):
        mllist = [mllist]

    for ml in mllist:
        o = ml.observations()
        o_nu = ml.oseries.series.drop(o.index)

        # add oseries
        if not o_nu.empty:
            trace_oseries_nu = go.Scattergl(
                x=o_nu.index,
                y=o_nu.values,
                mode="markers",
                marker={"color": "gray", "size": 3},
                name="(unused)",
                legendgroup=ml.oseries.name,
                showlegend=False,
            )
            trace_oseries = go.Scattergl(
                x=o.index,
                y=o.values,
                mode="markers",
                marker={"color": "black", "size": 5},
                name=ml.oseries.name,
                legendgroup="oseries",
            )
            traces.append(trace_oseries_nu)
            traces.append(trace_oseries)
        else:
            trace_oseries = go.Scattergl(
                x=o.index,
                y=o.values,
                mode="markers",
                marker_color="black",
                name=ml.oseries.name,
                legendgroup=ml.oseries.name,
            )
            traces.append(trace_oseries)

        sim = ml.simulate(tmin=tmin, tmax=tmax)
        trace_sim = go.Scattergl(
            x=sim.index,
            y=sim.values,
            mode="lines",
            # marker_color="#1F77B4",
            name=f"Sim (R<sup>2</sup> = {ml.stats.rsq():.3f})",
            legendgroup=ml.name,
        )
        traces.append(trace_sim)

        layout = {
            # "xaxis": {"range": [sim.index[0], sim.index[-1]]},
            "yaxis": {"title": "(m NAP)"},
            "legend": {
                "traceorder": "reversed+grouped",
                "orientation": "h",
                "xanchor": "left",
                "yanchor": "bottom",
                "x": 0.0,
                "y": 1.02,
            },
            "dragmode": "pan",
            "margin": {"t": 70, "b": 40, "l": 40, "r": 10},
        }

    return {"data": traces, "layout": layout}
