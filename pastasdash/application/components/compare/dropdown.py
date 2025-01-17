from dash import dcc

from pastasdash.application.components.shared import ids


def render(pstore, selected_data):
    placeholder_msg = "Select model(s), use map and table to filter models..."
    return dcc.Dropdown(
        id=ids.COMPARE_MODEL_SELECTION_DROPDOWN,
        options=[{"label": i, "value": i} for i in pstore.model_names],
        clearable=True,
        placeholder=placeholder_msg,
        value="no model",
        multi=True,
        searchable=True,
        disabled=False,
    )
