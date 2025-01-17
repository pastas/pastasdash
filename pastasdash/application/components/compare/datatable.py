from dash import dash_table, html
from dash.dash_table.Format import Format

from pastasdash.application.components.shared import ids
from pastasdash.application.components.shared.styling import DATA_TABLE_HEADER_BGCOLOR
from pastasdash.application.datasource import PastaStoreInterface


def render_metadata_table(pstore: PastaStoreInterface, selected_data=None):
    """Render the observation well data table.

    Parameters
    ----------
    pstore : PastaStoreInterface
        An interface to the data source containing the required data.
    selected_data : optional
        Data that is selected, by default None.

    Returns
    -------
    html.Div
        A Dash HTML Div component containing the rendered DataTable.

    Notes
    -----
    The table displays columns ['bro_id', 'nitg_code', 'tube_number',
    'screen_top', 'screen_bot', 'x', 'y', and 'metingen']. The table supports
    native filtering and sorting, and has fixed headers with virtualization
    enabled for better performance with large datasets. The style of the table
    and its cells is customized, including conditional styling for selected
    rows.
    """
    oseries = pstore.oseries.reset_index()

    oseries["n_models"] = [
        len(pstore.oseries_models.get(o, [])) for o in oseries["name"]
    ]

    usecols = [
        "id",
        "name",
        "x",
        "y",
        "screen_top",
        "screen_bot",
        "n_models",
    ]
    return html.Div(
        id="table-div",
        children=[
            dash_table.DataTable(
                id=ids.COMPARE_METADATA_TABLE,
                data=oseries.loc[:, usecols].to_dict("records"),
                columns=[
                    {
                        "id": "name",
                        "name": "Observation well",
                        "type": "text",
                    },
                    # {
                    #     "id": "nitg_code",
                    #     "name": "NITG",
                    #     "type": "text",
                    # },
                    # {
                    #     "id": "tube_number",
                    #     "name": "Filternummer",
                    #     "type": "numeric",
                    #     # "format": Format(scheme="r", precision=1),
                    # },
                    {
                        "id": "x",
                        "name": "X",
                        "type": "numeric",
                        "format": Format(scheme="r", precision=5),
                    },
                    {
                        "id": "y",
                        "name": "Y",
                        "type": "numeric",
                        "format": Format(scheme="r", precision=6),
                    },
                    {
                        "id": "screen_top",
                        "name": "Screen top",
                        "type": "numeric",
                        "format": {"specifier": ".2f"},
                    },
                    {
                        "id": "screen_bot",
                        "name": "Screen bottom",
                        "type": "numeric",
                        "format": {"specifier": ".2f"},
                    },
                    {
                        "id": "n_models",
                        "name": "N_models",
                        "type": "numeric",
                        "format": {"specifier": ".0f"},
                    },
                ],
                fixed_rows={"headers": True},
                page_action="none",
                filter_action="native",
                sort_action="native",
                style_table={
                    "height": "40vh",
                    # "overflowY": "auto",
                    "margin-top": 15,
                },
                row_selectable="multi",
                virtualization=True,
                selected_rows=oseries["id"].tolist(),
                style_cell={"whiteSpace": "pre-line", "fontSize": 12},
                style_cell_conditional=[
                    {
                        "if": {"column_id": c},
                        "textAlign": "left",
                    }
                    for c in ["name"]
                ]
                + [
                    {"if": {"column_id": "name"}, "width": "30%"},
                    # {"if": {"column_id": "nitg_code"}, "width": "10%"},
                    # {"if": {"column_id": "tube_number"}, "width": "10%"},
                    {"if": {"column_id": "x"}, "width": "10%"},
                    {"if": {"column_id": "y"}, "width": "10%"},
                    {"if": {"column_id": "screen_top"}, "width": "15%"},
                    {"if": {"column_id": "screen_bot"}, "width": "15%"},
                    {"if": {"column_id": "n_models"}, "width": "15%"},
                ],
                style_data_conditional=[
                    {
                        "if": {"state": "selected"},  # 'active' | 'selected'
                        "border": "1px solid #006f92",
                    },
                ],
                style_header={
                    "backgroundColor": DATA_TABLE_HEADER_BGCOLOR,
                    "fontWeight": "bold",
                },
            ),
        ],
        className="dbc dbc-row-selectable",
    )


def render_parameters_table():
    return html.Div(
        dash_table.DataTable(
            id=ids.COMPARE_PARAMETERS_TABLE,
            style_cell={"whiteSpace": "pre-line", "fontSize": 10},
            style_cell_conditional=[
                {
                    "if": {"column_id": c},
                    "textAlign": "left",
                    "width": "30%",
                }
                for c in ["parameter"]
            ],
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": DATA_TABLE_HEADER_BGCOLOR,
                }
            ],
            style_header={
                "backgroundColor": DATA_TABLE_HEADER_BGCOLOR,
                "fontWeight": "bold",
            },
            style_table={
                # "height": "25vh",
                "margin-top": "1vh",
                "overflowY": "auto",
            },
        ),
    )


def render_modelchecks_table():
    return html.Div(
        dash_table.DataTable(
            id=ids.COMPARE_CHECKS_TABLE,
            style_cell={"whiteSpace": "pre-line", "fontSize": 10},
            style_cell_conditional=[
                {
                    "if": {"column_id": c},
                    "textAlign": "left",
                    "width": "30%",
                }
                for c in ["index"]
            ],
            style_header={
                "backgroundColor": DATA_TABLE_HEADER_BGCOLOR,
                "fontWeight": "bold",
            },
            style_table={
                "height": "25vh",
                "overflowY": "auto",
            },
        ),
        style={"margin-top": "1vh"},
    )
