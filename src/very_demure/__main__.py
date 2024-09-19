# Standard Library
import logging
import signal
import sys
from pathlib import Path

# Third Party
import boto3
from dotenv import load_dotenv
from openai import OpenAI

# Our Libraries
from very_demure.openai import generate_mindfulness_script
from very_demure.polly import synthesize_speech
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

    engine = cli_args.get("engine", "neural")
    voice = cli_args.get("voice", "Matthew")
    duration = cli_args.get("duration", "1")

    output_name = f"{engine}-{voice}-{duration}"

    openai_client = OpenAI()

    script = generate_mindfulness_script(client=openai_client, engine=engine, duration=duration)
    logger.info(script.content)
    exact_script = script.content.split("[SCRIPT]")[1]
    logger.info(exact_script)

    transcript_file = Path(f"{output_name}.txt")
    transcript_file.write_text(exact_script)

    boto3_session = boto3.Session()
    polly_client = boto3_session.client("polly", region_name="us-east-1")

    # voice_id = "Amy|Ruth|Matthew"
    synthesize_speech(
        exact_script, engine=engine, voice_id=voice, output_file=f"{output_name}.mp3", polly_client=polly_client
    )


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
