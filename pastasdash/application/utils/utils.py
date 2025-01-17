import os
import tempfile
from contextlib import contextmanager

import numpy as np
from pyproj import Transformer


def conditional_decorator(dec, condition, **kwargs):
    def decorator(func):
        if not condition:
            # Return the function unchanged, not decorated.
            return func
        return dec(**kwargs)(func)

    return decorator


def get_plotting_zoom_level_and_center_coordinates(longitudes=None, latitudes=None):
    """Get zoom level and center coordinate for ScatterMap.

    Basic framework adopted from Krichardson under the following thread:
    https://community.plotly.com/t/dynamic-zoom-for-mapbox/32658/7
    Returns the appropriate zoom-level for these plotly-mapbox-graphics along with
    the center coordinate tuple of all provided coordinate tuples.

    Parameters
    ----------
    longitudes : array, optional
        longitudes
    latitudes : array, optional
        latitudes

    Returns
    -------
    zoom : float
        zoom level
    dict
        dictionary containing lat/lon coordinates of center point.
    """
    # Check whether both latitudes and longitudes have been passed,
    # or if the list lenghts don't match
    if (latitudes is None or longitudes is None) or (len(latitudes) != len(longitudes)):
        # Otherwise, return the default values of 0 zoom and the coordinate
        # origin as center point
        return 0, (0, 0)

    # Get the boundary-box
    b_box = {}
    b_box["height"] = latitudes.max() - latitudes.min()
    b_box["width"] = longitudes.max() - longitudes.min()
    b_box["center"] = {"lon": np.mean(longitudes), "lat": np.mean(latitudes)}

    # get the area of the bounding box in order to calculate a zoom-level
    area = b_box["height"] * b_box["width"]

    # * 1D-linear interpolation with numpy:
    # - Pass the area as the only x-value and not as a list, in order to return a
    #   scalar as well
    # - The x-points "xp" should be in parts in comparable order of magnitude of the
    #   given area
    # - The zoom-levels are adapted to the areas, i.e. start with the smallest area
    #   possible of 0 which leads to the highest possible zoom value 20, and so forth
    #   decreasing with increasing areas as these variables are antiproportional
    zoom = np.interp(
        x=area,
        xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
        fp=[20, 15, 14, 13, 12, 7, 5],
    )

    zoom = min([zoom, 15])  # do not use zoom 20

    # Finally, return the zoom level and the associated boundary-box center coordinates
    # NOTE: manual correction to view all of obs because of non-square window/extent?.
    return zoom, b_box["center"]


def get_transformer(crs_from, crs_to):
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=False)
    return transformer


def add_latlon_to_dataframe(
    df, crs_from="epsg:28992", crs_to="epsg:4236", x_col="x", y_col="y"
):
    transformer = get_transformer(crs_from, crs_to)
    latlon = np.vstack(transformer.transform(df[x_col].values, df[y_col].values)).T
    df["lat"] = latlon[:, 0]
    df["lon"] = latlon[:, 1]
    return df


def derive_input_parameters(v, precision=2):
    """Derive form parameters based on the type and value of the input.

    Parameters
    ----------
    v : any
        The input value to derive form parameters from. It can be of any type including
        tuple, callable, float, int, np.integer, str, or other types.

    Returns
    -------
    v : str or int
        The processed value, converted to a string if necessary.
    input_type : str
        The type of input, either "text" or "number".
    step : float or int or str or None
        The step value for numeric inputs, or "any" for text inputs, or None if
        not applicable.

    Notes
    -----
    - If `v` is a float, the input type is "number" and the step is calculated based
      on the number of decimals.
    - If `v` is an integer, the input type is "number" and the step is calculated based
      on the magnitude of the value.
    - If `v` is a string, the input type is "text" and the step is set to "any".
    - For other types, the input is converted to a string.
    """
    input_type = "text"
    ndecimals = None
    step = None

    if isinstance(v, float):
        input_type = "number"
        if np.floor(np.log10(np.abs(v))) <= -2:
            vstr = f"{v:.{precision}e}"
        elif np.floor(np.log10(np.abs(v))) > 5:
            vstr = f"{v:.{precision}e}"
        else:
            vstr = f"{v:.{precision}f}"
        ndecimals = len(vstr) - vstr.find(".") - 1
        step = 10 ** (-ndecimals) / 2
        v = float(vstr)
    elif isinstance(v, (int, np.integer)):
        input_type = "number"
        step = int(np.min([10 ** np.floor(np.log10(np.abs(v))), 10]))
        if isinstance(v, bool):
            v = int(v)
    elif isinstance(v, str):
        input_type = "text"
        step = "any"
    else:
        input_type = "text"
        step = None
        v = str(v)

    return v, input_type, step


@contextmanager
def temporary_file(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(data)
    temp.close()
    try:
        yield temp.name
    finally:
        os.unlink(temp.name)
