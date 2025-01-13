import functools

import numpy as np
import pandas as pd
import pastastore as pst
import pyproj
from tqdm import tqdm

from pastasdash.application.utils import add_latlon_to_dataframe

# TODO:
# Add lat/lon to metadata tables
# Ensure x, y coordinates provided
# Ensure screen_top, screen_bot for oseries?
# Compute tmin/tmax,n_obs for oseries (and stresses)


class PastaStoreInterface:
    """PastaStoreInterface object is a thin wrapper around PastaStore.

    Facilitates the communication between the application and the PastaStore database.
    """

    def __init__(
        self,
        pstore,
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
        self._register_pastastore_methods()

    def _register_pastastore_methods(self):
        """Register PastaStore methods to PastaStoreInterface object."""
        to_register = [
            func_or_attr
            for func_or_attr in dir(self.pstore)
            if (not func_or_attr.startswith("_")) and func_or_attr not in dir(self)
        ]

        for obj in to_register:
            setattr(self, obj, getattr(self.pstore, obj))

    @property
    def oseries(self):
        oseries = self.pstore.oseries.copy()
        oseries["id"] = np.arange(oseries.index.size)
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
        return oseries

    @property
    def stresses(self):
        stresses = self.pstore.stresses.copy()
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
        return stresses


class Interface:
    def __init__(self, store, column_dict=None, crs="epsg:28992"):
        """Initialize DashHelper for setting up data for the PastaStore Dashboard.

        Parameters
        ----------
        store : pastastore.PastaStore
            PastaStore instance
        column_dict : dict, optional
            dict containing custom column names (as keys) corresponding to
            required columns (as values) for dashboard. The dashboard requires
            the 'x', 'y', 'ftop' (screen/filter top), 'fbot' (screen/filter
            bottom), to be provided. If not provided, 'lat', 'lon', 'z' will be
            calculated.
        crs : str, optional
            crs string, by default "epsg:28992"
        """
        self.pstore = store
        self.oseries = self.pstore.oseries.copy()

        if column_dict is None:
            missing_cols = self.REQ_COLS.difference(self.oseries.columns)
        else:
            missing_cols = self.REQ_COLS.difference(
                column_dict.values().difference(self.oseries.columns)
            )
            self.oseries.rename(columns=column_dict, inplace=True)

        if len(missing_cols) > 0:
            raise ValueError(
                f"Oseries metadata is missing the following columns: {missing_cols}!"
            )

        # lat/lon
        self.oseries.loc[:, ["lat", "lon"]] = self.get_lat_lon(self.oseries, crs=crs)

        # replace inf with NaN
        self.oseries.replace(np.inf, np.nan, inplace=True)

        # calculate plotting depth z
        if "z" not in self.oseries.columns:
            self.oseries["z"] = self.oseries.loc[:, ["ftop", "fbot"]].mean(axis=1)

        # calculate no. of models per location
        self.oseries["nmodels"] = (
            self.oseries.reset_index()["name"]
            .apply(lambda o: len(self.pstore.oseries_models.get(o, [])))
            .values
        )

        # location
        # TODO: location/filter is not very general... maybe remove?
        if "location" not in self.oseries.columns:
            self.oseries["location"] = self.oseries.index.to_series().apply(
                lambda s: s.split("-")[-1] if "-" in s else s.split("_")[0]
            )
        if "filter" not in self.oseries.columns:

            def filternumber(s):
                filt = s.split("-")[-1] if "-" in s else s.split("_")[-1]
                try:
                    filt = int(filt)
                except ValueError:
                    filt = np.nan
                return filt

            self.oseries["filter"] = self.oseries.index.to_series().apply(
                lambda s: filternumber(s)
            )

        # get tim/tmax
        otmintmax = self.pstore.get_tmin_tmax("oseries")
        self.oseries = self.oseries.join(otmintmax)

        # sort oseries ascending
        self.oseries.sort_values(["location", "z"], ascending=True, inplace=True)

        # add unique ID
        self.oseries["id"] = np.arange(self.oseries.shape[0])

        # stresses lat/lon
        self.stresses = self.pstore.stresses.copy()
        self.stresses.loc[:, ["lat", "lon"]] = self.get_lat_lon(self.stresses, crs=crs)

    @staticmethod
    def get_lat_lon(df, crs):
        """Get lat/lon in EPSG:4236.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing x/y or lat/lon data.
        crs : str
            CRS string

        Returns
        -------
        np.ndarray
            array containing lat/lon columns
        """
        if not np.isin(["lat", "lon"], df.columns).all() or (crs != "epsg:4326"):
            transformer = pyproj.Transformer.from_crs(crs, "epsg:4326", always_xy=False)
            latlon = np.vstack(transformer.transform(df["x"].values, df["y"].values)).T
        elif crs is None:
            raise ValueError("Please provide CRS information, e.g. 'epsg:4236'")

        return latlon

    @property
    @functools.lru_cache  # noqa: B019, TODO: figure out how to remove this warning
    def model_checks(self):
        """Calculate or load model checks."""
        try:
            results_table = pd.read_csv(
                f"./data/modelchecks_{self.pstore.name}.csv", index_col=[0]
            )
        except FileNotFoundError:
            results_table = pd.DataFrame(
                index=self.pstore.model_names,
                columns=[
                    "r2",
                    "aic",
                    "rsq",
                    "acf",
                    "t_95",
                    "gain",
                    "bounds",
                    "accepted",
                ],
            )

            checks = pst.util.frontiers_checks(self.pstore)

            for mlnam in tqdm(self.pstore.model_names, desc="Checking models"):
                if mlnam not in checks.index:
                    continue

                idf = checks.loc[mlnam].dropna().astype(bool)

                results_table.loc[mlnam, "rsq"] = idf.loc["rsq >= threshold"]
                results_table.loc[mlnam, "acf"] = idf.loc["ACF: Runs test"]
                results_table.loc[mlnam, "bounds"] = idf.loc[
                    idf.index.str.startswith("Parameter")
                ].all()
                if (
                    idf.index.str.startswith("calib_period")
                    & idf.index.str.endswith("recharge")
                ).sum() > 0:
                    tmem_rch = idf.loc[
                        idf.index.str.startswith("calib_period")
                        & idf.index.str.endswith("recharge")
                    ].all()
                else:
                    tmem_rch = True
                if (
                    idf.index.str.startswith("calib_period")
                    & idf.index.str.contains("wells")
                ).sum() > 0:
                    tmem_wel = (
                        (
                            idf.loc[
                                idf.index.str.startswith("calib_period")
                                & idf.index.str.contains("wells")
                            ]
                        ).sum()
                        > 2
                    )
                else:
                    tmem_wel = True
                results_table.loc[mlnam, "t_95"] = tmem_rch and tmem_wel
                results_table.loc[mlnam, "gain"] = idf.loc[
                    idf.index.str.startswith("gain")
                ].all()

                # accepted.loc[mlnam, :] = idf["check_passed"].dropna().all()
                results_table.loc[mlnam, "accepted"] = (
                    idf.loc["rsq >= threshold"]
                    and idf.loc["ACF: Runs test"]
                    and idf.loc[idf.index.str.startswith("Parameter")].all()
                    and tmem_rch
                    and tmem_wel
                    and idf.loc[idf.index.str.startswith("gain")].all()
                )

            stats = self.pstore.get_statistics(["rsq"], progressbar=True)
            results_table = results_table.assign(r2=stats)

            aic = pst.util.frontiers_aic_select(
                self.pstore, modelnames=self.pstore.model_names, full_output=True
            )
            aic = aic.reset_index().set_index("modelname")
            if aic["dAIC"].isna().all():
                results_table = results_table.assign(aic=aic["AIC"])
                results_table = results_table.assign(location=aic["oseries"])

            results_table.to_csv(f"./data/modelchecks_{self.pstore.name}.csv")

        return results_table
