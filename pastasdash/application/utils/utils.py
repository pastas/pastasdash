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
    return zoom + 3, b_box["center"]


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
