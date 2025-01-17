import argparse
import sys

from pastasdash.application.main import run_dashboard
from pastasdash.application.settings import settings


def cli_main():
    """PastasDash dashboard command-line interface.

    Usage
    -----
    Run Dashboard with::

        pastasdash [--debug BOOL] [--port PORT]
    """
    parser = argparse.ArgumentParser(
        description="Run PastasDash dashboard on localhost.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Note: To configure the dashboard see the "
            "pastasdash/application/config.toml file."
        ),
    )

    parser.add_argument(
        "--debug",
        type=bool,
        default=settings["DEBUG"],
        help=f"Run app in debug mode (default: {settings['DEBUG']})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=settings["PORT"],
        help=f"Port to run the dashboard on (default: {settings['PORT']})",
    )

    kwargs = vars(parser.parse_args())

    try:
        run_dashboard(**kwargs)
    except (EOFError, KeyboardInterrupt):
        sys.exit(f" cancelling '{sys.argv[0]}'")
