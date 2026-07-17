"""Punto de entrada del daemon (entry point `daemon` de poetry)."""
import os

from dotenv import load_dotenv

from aia_utils.logs_cfg import config_logger
from aia_utils.toml_utils import getVersion

import logging

load_dotenv()
config_logger()
logger = logging.getLogger(__name__)

from aia_device.web.app import create_app

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9006"))


def run():
    version = getVersion()
    logger.info(f"Running nara-monitor daemon v{version}")
    app = create_app()
    app.run(host=HOST, port=PORT, threaded=True)


if __name__ == "__main__":
    run()

