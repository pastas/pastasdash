The PastasDash dashboard can be used to interactively view time series model results.

Load a PastaStore by clicking the "Load Pastastore" button at the top-right of the page.
Both .pastastore and .zip-files are supported.

> **Note:** PastasDash is currently experimental and under active
development. If you run into any issues, or even better, have a solution for a
specific issue, please report them on GitHub. See the link to the PastasDash
homepage in the References section below.

---

### Overview tab

The overview tab consists of three elements:

* Interactive map view showing measurement locations (top left)
* Interactive table showing measurement location metadata (top right)
* Interactive chart showing time series (bottom)

There are two ways of plotting time series:

* Select one or multiple (up to 20) measurement locations on the map using your
  mouse or the rectangle selection tool.
* (Shift+)Click on row(s) in the table.

### Time Series Models tab

The time series models tab allows users to create or inspect time series models
using Pastas and Pastastore. The calibration period for models can be adjusted.
Re-calibrated models can be saved in the pastastore.

* The left plot shows the model results figure (simulated heads, model
parameters, residuals, contributions and response functions for each
stressmodel).
* The right plot shows the model diagnostics plot, including the
noise/residuals an autocorrelation plot, a normality plot, and
heteroscedasticity plots.

### Compare Models tab

The compare models tab allows comparison of model simulations, parameters and checks.

Select models to compare from the top-right dropdown. The models available for
selection in the dropdown are controlled by the map and table on the left.
Selecting points on the map (with the rectangle selection tool or clicking on
the map) will filter the table. Use the checkboxes to select observation wells.
The time series models for each of these observations wells are included in the
dropdown menu.

The chart shows the model simulation(s) and the observed heads. The tables
below show the model parameters and the results of several model checks,
respectively. The default checks that are performed:

* $R^2 \geq 0.7$
* Response $t_{95}$ < 0.5 $\cdot$ calibration period
* The [Runs test](https://en.wikipedia.org/wiki/Wald%E2%80%93Wolfowitz_runs_test) for significant autocorrelation
* The parameters are smaller than $2\sigma$
* The parameters are on the bounds

### Map Results tab

The map results tab allows the user to generate maps with certain statistics. Supported
statistics are:

* Model parameters
* [Fit metrics](https://pastas.readthedocs.io/stable/api/generated/generated/pastas.stats.metrics.html) (e.g. $R^2$, EVP, RMSE, etc.)
* [Signatures](https://pastas.readthedocs.io/stable/examples/signatures.html) (e.g. `avg_seasonal_fluctuation`, `mean_annual_maximum`, etc.)

Additional options to style the map include colormap selection, minimum and
maximum values for constraining the colormap.

Pressing the "Generate Map" button will start the process of generating the
map. Producing the first map for a parameter can take some time, as the results
have to be computed for all models or time series. These results are cached, so
subsequent calls to "Generate Map", for example to adjust colorbar settings,
will be fast.

The "Download data" button will download the map and head time series data as a
CSV file.

### References

* Documentation for [pastas](https://pastas.dev/)
* Documentation for [pastastore](https://pastastore.readthedocs.io/en/latest/)
* Homepage for [pastasdash](https://github.com/pastas/pastasdash.git)
