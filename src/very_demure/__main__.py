# Standard Library
import logging
import signal
import sys

# Third Party
from dotenv import load_dotenv

# Our Libraries
from very_demure.utils import (
    CLI_ARGS_CONFIG,
    ISO8601_DATE_FORMAT,
    LOG_FORMAT,
    cli_handle_args,
    handleSigINTTERMKILL,
)

load_dotenv()

logger = logging.getLogger(__name__)

signal.signal(signal.SIGTERM, handleSigINTTERMKILL)
signal.signal(signal.SIGINT, handleSigINTTERMKILL)


def main() -> None:
    """Entrypoint for processing inference job."""
    cli_args = cli_handle_args(CLI_ARGS_CONFIG, sys.argv[1:])
    logger.info(cli_args)


def graceful_shutdown_handler(e: Exception) -> None:
    """Respond to SIGINT/SIGTERM signals to gracefully shutdown."""
    logger.warning("Gracefully shutting down.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=ISO8601_DATE_FORMAT)
    try:
        main()
    except KeyboardInterrupt:  # SIGINT
        logger.error("Recieved SIGINT. Terminating gracefully.")
    except Exception as e:
        logger.error(e)
        graceful_shutdown_handler(e)
        raise e
