from itertools import chain

import pandas as pd
import pastas as ps
from dash import Input, Output, State, ctx
from dash.dash_table.Format import Format
from dash.exceptions import PreventUpdate

from pastasdash.application.components.compare.chart import plot_model_comparison
from pastasdash.application.components.overview.mapview import plot_mapview
from pastasdash.application.components.shared import ids, styling


def register_compare_callbacks(app, pstore):
    """Register the map callbacks.

    Parameters
    ----------
    app : object
        The application instance to which the callbacks will be registered.
    pstore : object
        The pastastore interface that will be used by the callbacks.
    """

    @app.callback(
        Output(ids.COMPARE_MAP, "figure"),
        Input(ids.COMPARE_METADATA_TABLE, "selected_cells"),
        prevent_initial_call=False,
    )
    def zoom_map_to_table_selection(selected_cells):
        """Zoom to location on click in oseries DataTable.

        Parameters
        ----------
        selectedCells : list of dict
            list of selected rows

        Returns
        -------
        dict
            map layout and mapdata dictionary zoomed to selected location(s)
        """
        # zoom to oseries in selected cell in datatable
        if selected_cells:
            selected_row_ids = [d["row_id"] for d in selected_cells]
            return plot_mapview(
                pstore,
                selected_data=selected_row_ids,
                update_extent=True,
            )
        else:
            raise PreventUpdate

    @app.callback(
        Output(ids.COMPARE_METADATA_TABLE, "data"),
        Output(ids.COMPARE_METADATA_TABLE, "selected_rows", allow_duplicate=True),
        Output(ids.COMPARE_METADATA_TABLE, "selected_row_ids", allow_duplicate=True),
        Input(ids.COMPARE_MAP, "selectedData"),
        prevent_initial_call=True,
    )
    def update_overview_table(data):
        """Update oseries DataTable from map selection or by filter.

        Parameters
        ----------
        data : dict
            dictionary containing selected points on map
        filter : str
            filter strings

        Returns
        -------
        dff : pd.DataFrame
            selected/filtered or all oseries data for table
        """
        oseries = pstore.oseries.copy()
        if data is not None:
            # set data

            # get selection
            if data is not None:
                pts = pd.DataFrame(data["points"])
            else:
                pts = None

            # get selected points
            if pts is not None and not pts.empty:
                idx = pts.loc[pts.curveNumber == 0, "pointNumber"].values
                oseries = oseries.reset_index(drop=("name" in oseries.columns)).set_index("id").loc[idx].reset_index()

            table = oseries.to_dict("records")
            selected_rows = [i for i, _ in enumerate(table)]
            selected_row_ids = list(oseries["id"])
            return table, selected_rows, selected_row_ids
        else:
            # necessary to return all options when selectedData is None
            return (
                oseries.reset_index(drop=("name" in oseries.columns)).to_dict("records"),
                list(range(oseries.index.size)),
                list(range(oseries.index.size)),
            )

    @app.callback(
        Output(ids.COMPARE_MODEL_SELECTION_DROPDOWN, "options"),
        Output(ids.COMPARE_MODEL_SELECTION_DROPDOWN, "disabled"),
        Input(ids.COMPARE_METADATA_TABLE, "selected_row_ids"),
        prevent_initial_call=True,
    )
    def get_locations_for_overview_dropdown(sel):
        """Get list of options for overview tab dropdown.

        Parameters
        ----------
        sel : list
            list of selected locations from datatable

        Returns
        -------
        list of dict, bool
            list of dropdown options, boolean indicating dropdown is active
        """
        if sel not in [None, []]:
            mask = pstore.oseries["id"].isin(sel)
            idx = pstore.oseries.loc[mask].index
            names = idx.tolist()
            modelnames = (pstore.oseries_models.get(n, []) for n in names)
            modelnames = list(chain.from_iterable(modelnames))
            if len(modelnames) > 0:
                return [{"label": i, "value": i} for i in modelnames], False
            else:
                return [{"label": "", "value": "no model"}], True
        else:
            return [{"label": "", "value": "no model"}], True

    @app.callback(
        Output(ids.COMPARE_MODELS_CHART, "figure"),
        Input(ids.COMPARE_MODEL_SELECTION_DROPDOWN, "value"),
    )
    def plot_model_comparison_from_dropdown(value):
        """Plot model simulation and observations.

        Parameters
        ----------
        value : list of str
            list of model name(s)

        Returns
        -------
        dict
            plotly model simulation plot
        """
        if value in ["no model", "", None, []]:
            return {"layout": {"title": "No model selected or found!"}}
        else:
            ml = pstore.get_models(value)
            if ml is not None:
                chart = plot_model_comparison(ml)
                return chart
            else:
                return {"layout": {"title": "No model selected or found!"}}

    @app.callback(
        Output(ids.COMPARE_PARAMETERS_TABLE, "columns"),
        Output(ids.COMPARE_PARAMETERS_TABLE, "data"),
        Input(ids.COMPARE_MODEL_SELECTION_DROPDOWN, "value"),
    )
    def set_model_params_table(value):
        """Set model parameters comparison datatable.

        Parameters
        ----------
        value : list of str
            list of model names

        Returns
        -------
        columns : list of dict
            datatable column names
        pdf : dict
            pandas DataFrame of parameters exported as records dict
        """
        if value in ["no model", "", None, []]:
            columns = [
                {"id": "parameter", "name": "Parameter", "type": "text"},
                {"id": "modelname", "name": "No model(s) selected", "type": "text"},
            ]
            pdf = pd.DataFrame(columns=["parameter", "modelname"]).to_dict("records")
            return columns, pdf
        else:
            params = []
            columns = [{"id": "parameter", "name": "Parameter", "type": "text"}]
            for val in value:
                ml = pstore.get_models(val)
                pdf = ml.parameters.loc[:, "optimal"].to_frame()
                pdf.columns = [val]
                params.append(pdf)
                columns.append(
                    {
                        "id": val,
                        "name": val,
                        "type": "numeric",
                        "format": Format(scheme="r", precision=4),
                    }
                )
            pdf = pd.concat(params, axis=1)
            pdf.index.name = "parameter"
            pdf.reset_index(inplace=True)
            pdf = pdf.to_dict("records")
            return columns, pdf

    @app.callback(
        Output(ids.COMPARE_CHECKS_TABLE, "columns"),
        Output(ids.COMPARE_CHECKS_TABLE, "data"),
        Output(ids.COMPARE_CHECKS_TABLE, "style_data_conditional"),
        Input(ids.COMPARE_MODEL_SELECTION_DROPDOWN, "value"),
    )
    def set_overview_model_checks_table(value):
        """Set model checks table.

        Parameters
        ----------
        value : list of str
            list of model names

        Returns
        -------
        columns : list of dict
            list of columns in datatable
        chkdf : dict
            pandas DataFrame of checks exported as records dict
        style_data : list of dict
            dict of conditional formatting statements
        """
        if value in ["no model", "", None, []]:
            columns = [
                {"id": "index", "name": "Checks", "type": "text"},
                {"id": "passed", "name": "No model(s) selected", "type": "text"},
            ]
            chkdf = pd.DataFrame(columns=["check", "passed"]).to_dict("records")
            return columns, chkdf, None
        else:
            columns = [{"id": "index", "name": "Checks", "type": "text"}]

            mllist = pstore.get_models(value)
            if isinstance(mllist, ps.Model):
                mllist = [mllist]

            check_dfs = []
            for ml in mllist:
                cdf = ps.check.checklist(
                    ml, ps.check.checks_brakenhoff_2022, report=False
                )["pass"].astype(str)
                cdf.name = ml.name
                check_dfs.append(cdf)
            chkdf = pd.concat(check_dfs, axis=1)
            chkdf.index.name = "index"

            for val in value:
                columns.append(
                    {
                        "id": val,
                        "name": val,
                        "type": "text",
                    }
                )
            style_data = [
                {
                    "if": {
                        "filter_query": '{{{}}} = "True"'.format(col),
                        "column_id": col,
                    },
                    "color": "DarkGreen",
                    "backgroundColor": styling.DATA_TABLE_TRUE_BGCOLOR,
                }
                for col in value
            ] + [
                {
                    "if": {
                        "filter_query": '{{{}}} = "False"'.format(col),
                        "column_id": col,
                    },
                    "color": "DarkRed",
                    "backgroundColor": styling.DATA_TABLE_FALSE_BGCOLOR,
                }
                for col in value
            ]

            chkdf = chkdf.reset_index().to_dict("records")
            return columns, chkdf, style_data

    @app.callback(
        Output(ids.COMPARE_METADATA_TABLE, "selected_rows", allow_duplicate=True),
        Output(ids.COMPARE_METADATA_TABLE, "selected_row_ids", allow_duplicate=True),
        Input(ids.COMPARE_TABLE_SELECT_ALL_BUTTON, "n_clicks"),
        Input(ids.COMPARE_TABLE_DESELECT_ALL_BUTTON, "n_clicks"),
        State(ids.COMPARE_METADATA_TABLE, "derived_virtual_data"),
        prevent_initial_call=True,
    )
    def select_all_in_table(click_select_all, click_clear, current_table):
        if click_select_all and ctx.triggered_id == ids.COMPARE_TABLE_SELECT_ALL_BUTTON:
            table = pd.DataFrame(current_table)
            return table["id"].tolist(), table["id"].tolist()
        elif click_clear and ctx.triggered_id == ids.COMPARE_TABLE_DESELECT_ALL_BUTTON:
            return [], []
        else:
            raise PreventUpdate
