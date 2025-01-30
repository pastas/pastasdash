import functools

import numpy as np
import pandas as pd
import pastastore as pst

from pastasdash.application.settings import settings
from pastasdash.application.utils import add_latlon_to_dataframe

# TODO:
# Ensure x, y coordinates provided
# Ensure screen_top, screen_bot for oseries?


def get_timeseries_stats(name, pstore):
    o = pstore.get_oseries(name)
    s = pd.Series(
        {
            "tmin": o.first_valid_index(),
            "tmax": o.last_valid_index(),
            "n_observations": o.index.size,
        }
    )
    s.index.name = name
    return s


class PastaStoreInterface:
    """PastaStoreInterface object is a thin wrapper around PastaStore.

    Facilitates the communication between the application and the PastaStore database.
    """

    def __init__(
        self,
        pstore=None,
        x="x",
        y="y",
        screen_top="screen_top",
        screen_bot="screen_bot",
        lat=None,
        lon=None,
        crs="epsg:28992",
    ):
        """Initialize PastaStoreInterface object.

        Parameters
        ----------
        pstore : pastastore.PastaStore
            PastaStore object
        """
        if pstore is None:
            self.pstore = pst.PastaStore()
        else:
            self.pstore = pstore

        self.column_mapping = {
            "x": x,
            "y": y,
            "screen_top": screen_top,
            "screen_bot": screen_bot,
        }
        if lat is None:
            self.column_mapping["lat"] = "lat"
        else:
            self.column_mapping["lat"] = lat
        if lon is None:
            self.column_mapping["lon"] = "lon"
        else:
            self.column_mapping["lon"] = lon

        self.crs = crs
        self.registered_funcs = []
        self._register_pastastore_methods()

    def set_pastastore(self, pstore):
        """Set PastaStore object.

        Parameters
        ----------
        pstore : pastastore.PastaStore
            PastaStore object
        """
        self.pstore = pstore
        # delete registered functions and attributes so they are overwritten by new
        # pastastore
        for func_or_attr in self.registered_funcs:
            if hasattr(self, func_or_attr):
                delattr(self, func_or_attr)
        self._check_pastastore_metadata()
        self._register_pastastore_methods()

    def _check_pastastore_metadata(self):
        """Check if required metadata is in PastaStore."""
        msg = "Required metadata not found in PastaStore. "
        raise_error = False
        missing_cols = []
        for k, v in self.column_mapping.items():
            if v not in self.pstore.oseries.columns:
                # msg += f"\n - No column '{v}' representing '{k}' found in oseries."
                missing_cols.append(f"{k}:{v}")
                raise_error = True
        msg += "Missing (name:expected name): " + ", ".join(missing_cols) + " "
        msg += (
            "\nTo fix, modify the default kwargs in PastaStoreInterface in "
            "'pastasdash/application/datasource/datasource.py'. We are working "
            "on a more user-friendly solution."
        )
        if raise_error:
            raise ValueError(msg)

    def _register_pastastore_methods(self):
        """Register PastaStore methods to PastaStoreInterface object."""
        to_register = [
            func_or_attr
            for func_or_attr in dir(self.pstore)
            if (not func_or_attr.startswith("_")) and func_or_attr not in dir(self)
        ]
        self.registered_funcs = to_register

        for obj in to_register:
            setattr(self, obj, getattr(self.pstore, obj))

    @functools.lru_cache()  # noqa: B019
    def oseries_stats(self, oseries_names):
        return self.pstore.apply(
            "oseries",
            get_timeseries_stats,
            names=oseries_names,
            kwargs={"pstore": self.pstore},
            parallel=settings["PARALLEL"],
            fancy_output=True,
        ).T

    @property
    def oseries(self):
        oseries = self.pstore.oseries.copy()
        if not oseries.empty:
            if (
                self.column_mapping["lat"] not in oseries.columns
                or self.column_mapping["lon"] not in oseries.columns
            ):
                oseries = add_latlon_to_dataframe(
                    oseries,
                    crs_from=self.crs,
                    x_col=self.column_mapping["x"],
                    y_col=self.column_mapping["y"],
                )
            oseries["kind"] = "oseries"

            oseries["z"] = oseries.loc[:, ["screen_top", "screen_bot"]].mean(axis=1)
            oseries.sort_values("z", ascending=True, inplace=True)
            oseries["id"] = np.arange(oseries.index.size)
            oseries = oseries.join(self.oseries_stats(tuple(self.pstore.oseries_names)))
        else:
            oseries = pd.DataFrame(
                columns=[
                    "kind",
                    "x",
                    "y",
                    "z",
                    "lat",
                    "lon",
                    "screen_top",
                    "screen_bot",
                    "id",
                    "n_observations",
                    "tmin",
                    "tmax",
                ]
            )
            oseries.index.name = "name"
        return oseries

    @property
    def stresses(self):
        stresses = self.pstore.stresses.copy()
        if not stresses.empty:
            stresses["id"] = np.arange(stresses.index.size)
            if (
                self.column_mapping["lat"] not in stresses.columns
                or self.column_mapping["lon"] not in stresses.columns
            ):
                stresses = add_latlon_to_dataframe(
                    stresses,
                    crs_from=self.crs,
                    x_col=self.column_mapping["x"],
                    y_col=self.column_mapping["y"],
                )
        else:
            stresses = pd.DataFrame(columns=["kind", "x", "y", "lat", "lon", "id"])
            stresses.index.name = "name"
        return stresses

    @property
    @functools.lru_cache  # noqa: B019
    def unique_parameters(self):
        param_set = set()
        for mldict in self.pstore.get_models(None, return_dict=True):
            param_set |= set(mldict["parameters"].index)
        return list(param_set)

    @property
    def timeseries(self):
        usecols = ["id", "kind", "x", "y", "lat", "lon", "screen_top", "screen_bot"]
        df = pd.concat([self.oseries, self.stresses])
        df["id"] = np.arange(df.index.size)
        return df[usecols]
