from pathlib import Path

import tomli

# %% load settings
PASTASDASH_APP_ROOT = Path(__file__).parent.parent
PASTASDASH_APP_PATH = Path(__file__).parent

with open(PASTASDASH_APP_PATH / "config.toml", "rb") as f:
    config = tomli.load(f)
    settings = config["settings"]

# %% set paths accordingly

ASSETS_PATH = PASTASDASH_APP_PATH / ".." / "assets"
CUSTOM_CSS_PATH = str(ASSETS_PATH / "custom.css")
