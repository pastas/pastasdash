from pastasdash.application.callbacks.compare import register_compare_callbacks
from pastasdash.application.callbacks.general import register_general_callbacks
from pastasdash.application.callbacks.maps import register_maps_callbacks
from pastasdash.application.callbacks.model import register_model_callbacks
from pastasdash.application.callbacks.overview import register_overview_callbacks


def register_callbacks(app, pstore):
    """Register all the necessary callbacks for the application.

    This function registers various callback functions to the provided app instance.
    It organizes the registration into several categories.

    Parameters
    ----------
    app : object
        The application instance to which the callbacks will be registered.
    pstore : object
        The pastastore interface that will be used by the callbacks.
    """
    register_general_callbacks(app, pstore)
    register_overview_callbacks(app, pstore)
    register_model_callbacks(app, pstore)
    register_compare_callbacks(app, pstore)
    register_maps_callbacks(app, pstore)
