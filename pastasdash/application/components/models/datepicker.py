from dash import dcc

from pastasdash.application.components.shared import ids
from pastasdash.application.datasource import PastaStoreInterface


def render_datepicker_tmin(pstore: PastaStoreInterface, selected_data):
    """Renders a DatePickerSingle component for selecting the minimum date (tmin).

    Parameters
    ----------
    pstore : PastaStoreInterface
        The database interface object.
    selected_data : list or None
        A list containing the selected data. If the list contains exactly one
        item, the function will attempt to retrieve the tmin date for that
        item. If None or the list length is not 1, the date picker will be
        disabled.

    Returns
    -------
    dcc.DatePickerSingle
        A Dash DatePickerSingle component for selecting a start time.
    """
    if selected_data is not None and len(selected_data) == 1:
        name = selected_data[0]
        try:
            tmintmax = pstore.get_tmin_tmax("oseries", name)
            start_date = tmintmax.loc[name, "tmin"].to_pydatetime()
            disabled = False
        except Exception:
            start_date = None
            disabled = True
    else:
        start_date = None
        disabled = True

    return dcc.DatePickerSingle(
        date=start_date,
        placeholder="Start date",
        display_format="YYYY-MM-DD",
        show_outside_days=True,
        number_of_months_shown=1,
        day_size=30,
        disabled=disabled,
        id=ids.MODEL_DATEPICKER_TMIN,
        style={"fontSize": 8},
    )


def render_datepicker_tmax(pstore, selected_data):
    """Renders a DatePickerSingle component for selecting the maximum date (tmax).

    Parameters
    ----------
    data : object
        The data object containing the `pstore` attribute, which provides
        access to the `get_tmin_tmax` method.
    selected_data : list or None
        A list containing the selected data. If the list contains exactly one
        item, the function will attempt to retrieve the tmax date for that
        item. If None or the list length is not 1, the date picker will be
        disabled.

    Returns
    -------
    dcc.DatePickerSingle
        A Dash DatePickerSingle component for selecting a end time.
    """
    if selected_data is not None and len(selected_data) == 1:
        name = selected_data[0]
        try:
            tmintmax = pstore.get_tmin_tmax("oseries", name)
            end_date = tmintmax.loc[name, "tmax"].to_pydatetime()
            disabled = False
        except Exception:
            end_date = None
            disabled = True
    else:
        end_date = None
        disabled = True

    return dcc.DatePickerSingle(
        date=end_date,
        placeholder="End date",
        display_format="YYYY-MM-DD",
        show_outside_days=True,
        number_of_months_shown=1,
        day_size=20,
        disabled=disabled,
        id=ids.MODEL_DATEPICKER_TMAX,
        style={"fontSize": 8},
    )
