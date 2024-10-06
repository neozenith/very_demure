# Utility functions

# Standard Library
import argparse
import logging
import os
import sys
from typing import Any

# Third Party
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

LOG_FORMAT: str = "%(levelname)s|%(asctime)s|%(filename)s:%(lineno)d - %(message)s"
JSON_LOG_FORMAT: str = (
    '{"level": "%(levelname)s", "time": "%(asctime)s",'
    '"file": "%(pathname)s", "line": %(lineno)d, "message": "%(message)s"}'
)
ISO8601_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

ENV_PREFIX = "VERYDEMURE_"
CLI_ARGS_CONFIG = {
    "duration": None,
    "voice": "Matthew",
    "engine": "neural",
    "output-location": "./output/",
    "provider": "bedrock",
    "model": "amazon.titan-text-premier-v1:0",
    "speed": "slow",
}


def sanitise_model_name(model_name: str) -> str:
    return model_name.replace(":", "_").replace(".", "_").replace("-", "_")


def __argparse_factory(config: dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    for flag, flag_kwargs in config.items():
        lowered_flag = flag.lower()
        short_flag = f"-{lowered_flag[0]}"
        long_flag = f"--{lowered_flag}"
        if isinstance(type(flag_kwargs), dict):
            parser.add_argument(short_flag, long_flag, **flag_kwargs)
        else:
            parser.add_argument(short_flag, long_flag, default=flag_kwargs)
    return parser


def cli_handle_args(config: dict[str, Any], args: list[str]) -> dict[str, Any]:
    """Parse the result of ArgumentParser into a dict."""
    parser = __argparse_factory(config)
    return vars(parser.parse_args(args))


def cli_resolve_env_var(key: str, env_var_prefix: str = ENV_PREFIX) -> str | None:
    """Attempt to resolve namespaced environment variable."""
    logger.info(env_var_prefix.upper() + key.upper())
    value = os.getenv(env_var_prefix.upper() + key.upper())
    logger.info(value)
    return value


# Python function that captures SIGTERM


def handleSigINTTERMKILL(signum, frame):
    print("application received SIG signal: " + str(signum))
    print("Cleaning up resources")
    # Code for cleaning up resources goes here

    print("exiting the container gracefully")
    # You can at this point use the sys.exit() to exit the program, or
    # continue on with the rest of the code.
    sys.exit(signum)
