import json
import os

import pandas as pd
import pastas as ps
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from pastas.extensions import register_plotly
from pastas.io.pas import PastasEncoder

from pastasdash.application.components.shared import ids

register_plotly()


def register_model_callbacks(app, pstore):
    @app.callback(
        Output(ids.MODEL_RESULTS_CHART, "figure", allow_duplicate=True),
        Output(ids.MODEL_DIAGNOSTICS_CHART, "figure", allow_duplicate=True),
        Output(ids.MODEL_SAVE_BUTTON, "disabled", allow_duplicate=True),
        Output(ids.ALERT_PLOT_MODEL_RESULTS, "data"),
        Output(ids.MODEL_DATEPICKER_TMIN, "date"),
        Output(ids.MODEL_DATEPICKER_TMAX, "date"),
        Output(ids.MODEL_DATEPICKER_TMIN, "disabled"),
        Output(ids.MODEL_DATEPICKER_TMAX, "disabled"),
        Input(ids.MODEL_DROPDOWN_SELECTION, "value"),
        prevent_initial_call=True,
    )
    def plot_model_results(value):
        """Plot the results and diagnostics of a time series model.

        Parameters
        ----------
        value : str or None
            The identifier of the model to be plotted. If None, no model is selected.

        Returns
        -------
        tuple
            A tuple containing:
            - plotly.graph_objs.Figure: The plotly figure of the model results.
            - plotly.graph_objs.Figure: The plotly figure of the model diagnostics.
            - bool: A flag indicating whether to activate model save button.
            - tuple: A tuple containing:
                - bool: A flag indicating if an alert should be shown.
                - str: The color of the alert ('success' or 'warning').
                - str: The alert message.
            - datetime.datetime or None: The minimum time of the model settings,
              or None if not available.
            - datetime.datetime or None: The maximum time of the model settings,
              or None if not available.

        Raises
        ------
        Exception
            If there is an error in retrieving or plotting the model.
        """
        # print(value)
        if value is not None:
            try:
                ml = pstore.get_models(value)
                print(value, ml)
                return (
                    ml.plotly.results(),
                    ml.plotly.diagnostics(),
                    False,
                    (
                        True,  # show alert
                        "success",  # alert color
                        f"Loaded time series model '{value}' from PastaStore.",
                    ),
                    ml.settings["tmin"].to_pydatetime(),
                    ml.settings["tmax"].to_pydatetime(),
                    False,
                    False,
                )
            except Exception as e:
                return (
                    {"layout": {"title": "No model"}},
                    {"layout": {"title": "No model"}},
                    True,
                    (
                        True,  # show alert
                        "warning",  # alert color
                        (f"No model available for {value}. " f"Error: {e}"),
                    ),
                    None,
                    None,
                    True,
                    True,
                )
        else:
            return (
                {"layout": {"title": "No model"}},
                {"layout": {"title": "No model"}},
                True,
                (
                    True,  # show alert
                    "success",  # alert color
                    "Did nothing",  # empty message
                ),
                None,
                None,
                True,
                True,
            )

    @app.callback(
        Output(ids.MODEL_RESULTS_CHART, "figure", allow_duplicate=True),
        Output(ids.MODEL_DIAGNOSTICS_CHART, "figure", allow_duplicate=True),
        Output(ids.PASTAS_MODEL_STORE, "data"),
        Output(ids.MODEL_SAVE_BUTTON, "disabled", allow_duplicate=True),
        Output(ids.ALERT_SOLVE_MODEL, "data"),
        Input(ids.MODEL_SOLVE_BUTTON, "n_clicks"),
        State(ids.MODEL_DROPDOWN_SELECTION, "value"),
        State(ids.MODEL_DATEPICKER_TMIN, "date"),
        State(ids.MODEL_DATEPICKER_TMAX, "date"),
        prevent_initial_call=True,
    )
    def solve_model(n_clicks, value, tmin, tmax):
        """Generate a time series model based on user input and update the stored copy.

        Parameters
        ----------
        n_clicks : int
            Number of clicks on the button that triggers the model generation.
        value : str
            Identifier for the time series in the format "gmw_id-tube_id".
        tmin : str
            Minimum timestamp for the model in a format recognized by `pd.Timestamp`.
        tmax : str
            Maximum timestamp for the model in a format recognized by `pd.Timestamp`.

        Returns
        -------
        tuple
            A tuple containing:
            - plotly.graph_objs._figure.Figure: Plotly figure of the model results.
            - plotly.graph_objs._figure.Figure: Plotly figure of the model diagnostics.
            - str: JSON representation of the generated model.
            - bool: Flag to enable or disable the save button.
            - tuple: Alert information containing:
                - bool: Flag to show or hide the alert.
                - str: Alert color ("success" or "danger").
                - str: Alert message.

        Raises
        ------
        PreventUpdate
            If `n_clicks` is None or `value` is None.
        """
        if n_clicks is not None:
            if value is not None:
                try:
                    tmin = pd.Timestamp(tmin)
                    tmax = pd.Timestamp(tmax)

                    # create model
                    ml = pstore.get_model(value)
                    ml.solve(tmin=tmin, tmax=tmax, report=False)
                    ml.add_noisemodel(ps.ArNoiseModel())
                    ml.solve(
                        freq="D",
                        tmin=tmin,
                        tmax=tmax,
                        report=False,
                        initial=False,
                    )
                    # store generated model
                    mljson = json.dumps(ml.to_dict(), cls=PastasEncoder)
                    return (
                        ml.plotly.results(tmin=tmin, tmax=tmax),
                        ml.plotly.diagnostics(),
                        mljson,
                        False,  # enable save button
                        (
                            True,  # show alert
                            "success",  # alert color
                            f"Created time series model for {value}.",
                        ),  # empty alert message
                    )
                except Exception as e:
                    return (
                        no_update,
                        no_update,
                        None,
                        True,  # disable save button
                        (
                            True,  # show alert
                            "danger",  # alert color
                            f"Error {e}",  # alert message
                        ),
                    )
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate

    @app.callback(
        Output(ids.ALERT_SAVE_MODEL, "data"),
        Input(ids.MODEL_SAVE_BUTTON, "n_clicks"),
        State(ids.PASTAS_MODEL_STORE, "data"),
        prevent_initial_call=True,
    )
    def save_model(n_clicks, mljson):
        """Save a model from a JSON string when a button is clicked.

        Parameters
        ----------
        n_clicks : int
            The number of times the save button has been clicked.
        mljson : str
            The JSON string representation of the model to be saved.

        Returns
        -------
        tuple
            A tuple containing a boolean indicating success, a string for the alert
            type, and a message string.

        Raises
        ------
        PreventUpdate
            If `n_clicks` is None or `mljson` is None.
        """
        if n_clicks is None:
            raise PreventUpdate
        if mljson is not None:
            with open("temp.pas", "w") as f:
                f.write(mljson)
            ml = ps.io.load("temp.pas")
            os.remove("temp.pas")
            try:
                pstore.add_model(ml, overwrite=True)
                return (
                    True,
                    "success",
                    f"Success! Saved model for {ml.oseries.name} in Pastastore!",
                )
            except Exception as e:
                return (
                    True,
                    "danger",
                    f"Error! Model for {ml.oseries.name} not saved: {e}!",
                )
        else:
            raise PreventUpdate
