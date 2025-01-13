# %%
import logging

import dash_bootstrap_components as dbc
import pastastore as pst
from dash import Dash

from pastasdash.application.cache import cache
from pastasdash.application.callbacks import register_callbacks
from pastasdash.application.components.layout import create_layout
from pastasdash.application.datasource import PastaStoreInterface
from pastasdash.application.settings import CUSTOM_CSS_PATH

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# %% set some variables
external_stylesheets = [
    dbc.themes.FLATLY,
    "https://use.fontawesome.com/releases/v6.5.1/css/all.css",
]

# %% create pastastore
conn = pst.PasConnector(
    name="zeeland_bro",
    path="/home/david/github/gwdatalens/gwdatalens/pastasdb/",
)
pstore = pst.PastaStore(conn)
ipstore = PastaStoreInterface(pstore)

# %% build app
# create app
app = Dash(
    "pastasdash",
    external_stylesheets=external_stylesheets + [CUSTOM_CSS_PATH],
    suppress_callback_exceptions=True,
)
app.title = "PastasDash"
app.layout = create_layout(app, ipstore)

# register callbacks
register_callbacks(app, ipstore)

# initialize cache
cache.init_app(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": ".cache",
    },
)

# %%
