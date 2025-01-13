from pathlib import Path

import tomli

# %% load settings
DATALENS_APP_ROOT = Path(__file__).parent.parent
DATALENS_APP_PATH = Path(__file__).parent

with open(DATALENS_APP_PATH / "config.toml", "rb") as f:
    config = tomli.load(f)
    settings = config["settings"]

# %% set paths accordingly

ASSETS_PATH = DATALENS_APP_PATH / ".." / "assets"
LOCALE_PATH = ASSETS_PATH / "locale"
CUSTOM_CSS_PATH = str(ASSETS_PATH / "custom.css")
