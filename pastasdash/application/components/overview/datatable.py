from dash import dash_table, html
from dash.dash_table.Format import Format

from pastasdash.application.components.shared import ids
from pastasdash.application.components.shared.styling import DATA_TABLE_HEADER_BGCOLOR
from pastasdash.application.datasource import PastaStoreInterface


def render(pstore: PastaStoreInterface, selected_data=None):
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
    oseries = pstore.oseries.reset_index(drop=("name" in pstore.oseries.columns))

    usecols = [
        "id",
        "name",
        # "nitg_code",
        # "tube_number",
        pstore.column_mapping["screen_top"],
        pstore.column_mapping["screen_bottom"],
        pstore.column_mapping["x"],
        pstore.column_mapping["y"],
        "n_observations",
        "tmin",
        "tmax",
    ]
    return html.Div(
        id="table-div",
        children=[
            dash_table.DataTable(
                id=ids.OVERVIEW_TABLE,
                data=oseries.loc[:, usecols].to_dict("records"),
                columns=[
                    {
                        "id": "name",
                        "name": "Name",
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
                        "id": pstore.column_mapping["x"],
                        "name": "X",
                        "type": "numeric",
                        "format": Format(scheme="r", precision=5),
                    },
                    {
                        "id": pstore.column_mapping["y"],
                        "name": "Y",
                        "type": "numeric",
                        "format": Format(scheme="r", precision=6),
                    },
                    {
                        "id": pstore.column_mapping["screen_top"],
                        "name": "Screen top",
                        "type": "numeric",
                        "format": {"specifier": ".2f"},
                    },
                    {
                        "id": pstore.column_mapping["screen_bottom"],
                        "name": "Screen bottom",
                        "type": "numeric",
                        "format": {"specifier": ".2f"},
                    },
                    {
                        "id": "tmin",
                        "name": "Start date",
                        "type": "datetime",
                    },
                    {
                        "id": "tmax",
                        "name": "End date",
                        "type": "datetime",
                    },
                    {
                        "id": "n_observations",
                        "name": "N_obs",
                        "type": "numeric",
                        "format": {"specifier": ".0f"},
                    },
                ],
                fixed_rows={"headers": True},
                page_action="none",
                filter_action="native",
                sort_action="native",
                style_table={
                    # "height": "45vh",
                    # "overflowY": "auto",
                    "margin-top": 15,
                },
                # row_selectable="multi",
                virtualization=True,
                style_cell={"whiteSpace": "pre-line", "fontSize": 12},
                style_cell_conditional=[
                    {
                        "if": {"column_id": c},
                        "textAlign": "left",
                    }
                    for c in ["name"]
                ]
                + [
                    {"if": {"column_id": "name"}, "width": "18%"},
                    # {"if": {"column_id": "nitg_code"}, "width": "10%"},
                    # {"if": {"column_id": "tube_number"}, "width": "10%"},
                    {"if": {"column_id": "x"}, "width": "7.5%"},
                    {"if": {"column_id": "y"}, "width": "7.5%"},
                    {"if": {"column_id": "screen_top"}, "width": "7.5%"},
                    {"if": {"column_id": "screen_bot"}, "width": "7.5%"},
                    {"if": {"column_id": "tmin"}, "width": "22.5%"},
                    {"if": {"column_id": "tmax"}, "width": "22.5%"},
                    {"if": {"column_id": "n_observations"}, "width": "7%"},
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
