import plotly.express as px
import plotly.graph_objects as go
from dash import dcc


def get_colormap_figures(source=px.colors.sequential):
    sequences = [
        (k, getattr(source, k))
        for k in dir(source)
        if not (k.startswith("_") or k.startswith("swatches") or k.endswith("_r"))
    ]

    n = 200

    cmap_dict = {}
    for name, _ in sequences:
        fig = dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        orientation="h",
                        y=[f"{name:<10s}"] * n,
                        x=[1] * n,
                        customdata=[(x + 1) / n for x in range(n)],
                        marker={
                            "color": list(range(n)),
                            "colorscale": name,
                            "line_width": 0,
                        },
                        hovertemplate="%{customdata}",
                        name=name,
                        width=1.0,
                    )
                ],
                layout={
                    "barmode": "stack",
                    "barnorm": "fraction",
                    "showlegend": False,
                    "xaxis": {
                        "range": [0.00, 1.00],
                        "showticklabels": False,
                        "showgrid": False,
                    },
                    "height": 30,
                    "width": 225,
                    "margin": {"l": 0, "r": 0, "t": 5, "b": 0},
                },
            ),
            config={"displayModeBar": False},
        )
        cmap_dict[name] = fig
    return cmap_dict


# DataTable styling constants:
DATA_TABLE_HEADER_BGCOLOR = "rgb(245, 245, 245)"
DATA_TABLE_ODD_ROW_BGCOLOR = "rgb(250, 250, 250)"
DATA_TABLE_FALSE_BGCOLOR = "rgb(255, 238, 238)"
DATA_TABLE_TRUE_BGCOLOR = "rgb(231, 255, 239)"
