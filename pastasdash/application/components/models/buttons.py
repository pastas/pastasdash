from dash import html
from dash_bootstrap_components import Button, Tooltip

from pastasdash.application.components.shared import ids


def render_solve_button():
    """Renders a button for generating time series models.

    Returns
    -------
    html.Div
        A Div containing the generate model button.
    """
    return html.Div(
        [
            Button(
                html.Span(
                    [
                        html.I(className="fa-solid fa-gear"),
                        " " + "Solve model",
                    ],
                    id="span-solve-model",
                    n_clicks=0,
                ),
                style={
                    "margin-top": 10,
                    "margin-bottom": 10,
                },
                disabled=False,
                id=ids.MODEL_SOLVE_BUTTON,
            ),
            Tooltip(
                children=[
                    html.P(
                        "Calibrate model between start (tmin) and end date (tmax).",
                        style={"margin-bottom": 0},
                    ),
                ],
                target=ids.MODEL_SOLVE_BUTTON,
                placement="right",
            ),
        ]
    )


def render_save_button():
    """Renders a save model button component.

    Returns
    -------
    div
        A Div containing the model save button.
    """
    return html.Div(
        [
            Button(
                html.Span(
                    [
                        html.I(className="fa-solid fa-floppy-disk"),
                        " " + "Save model",
                    ],
                    id="span-save-model",
                    n_clicks=0,
                ),
                style={
                    "margin-top": 10,
                    "margin-bottom": 10,
                },
                disabled=True,
                id=ids.MODEL_SAVE_BUTTON,
            ),
            Tooltip(
                children=[
                    html.P(
                        "Store calibrated model. Overwrites existing model.",
                        style={"margin-bottom": 0},
                    ),
                ],
                target=ids.MODEL_SAVE_BUTTON,
                placement="right",
            ),
        ]
    )
