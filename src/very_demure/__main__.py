# Standard Library
import logging
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Third Party
import boto3
from dotenv import load_dotenv
from openai import OpenAI

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

# Our Libraries
from very_demure.bedrock import (
    generate_mindfulness_script as bedrock_generate_mindfulness_script,
)
from very_demure.openai import (
    generate_mindfulness_script as openai_generate_mindfulness_script,
)
from very_demure.polly import synthesize_speech
from very_demure.utils import (
    CLI_ARGS_CONFIG,
    ISO8601_DATE_FORMAT,
    LOG_FORMAT,
    cli_handle_args,
    handleSigINTTERMKILL,
    sanitise_model_name,
)

load_dotenv()

logger = logging.getLogger(__name__)

signal.signal(signal.SIGTERM, handleSigINTTERMKILL)
signal.signal(signal.SIGINT, handleSigINTTERMKILL)


def main() -> None:
    """Entrypoint for processing inference job."""
    cli_args = cli_handle_args(CLI_ARGS_CONFIG, sys.argv[1:])
    logger.info(cli_args)

    provider = cli_args.get("provider", "bedrock")
    model = cli_args.get("model", "amazon.titan-text-premier-v1:0")
    engine = cli_args.get("engine", "neural")
    voice = cli_args.get("voice", "Matthew")
    duration = cli_args.get("duration", "1")

    model_name = sanitise_model_name(model)
    output_name = f"{provider}-{model_name}-{engine}-{voice}-{duration}"

    output_location = cli_args.get("output_location", "./output/")
    output_location_path = Path(output_location)
    logger.info(output_location_path)
    output_location_path.parent.mkdir(parents=True, exist_ok=True)

    openai_client = OpenAI()
    boto3_session = boto3.Session()
    polly_client = boto3_session.client("polly", region_name="us-east-1")
    bedrock_runtime_client: BedrockRuntimeClient = boto3_session.client("bedrock-runtime", region_name="us-east-1")
    logger.info("Clients created...")

    if provider == "openai":
        openai_script = openai_generate_mindfulness_script(client=openai_client, engine=engine, duration=duration)
        logger.info(openai_script.content)
        openai_exact_script = openai_script.content.split("[SCRIPT]")[1]
        logger.info(openai_exact_script)
        exact_script = openai_script

    elif provider == "bedrock":
        bedrock_script = bedrock_generate_mindfulness_script(
            client=bedrock_runtime_client, engine=engine, duration=duration
        )
        logger.info(bedrock_script)
        bedrock_exact_script = bedrock_script
        logger.info(bedrock_exact_script)
        exact_script = bedrock_script

    # Save a copy of the transcript
    transcript_file = output_location_path / f"{output_name}.txt"
    transcript_file.write_text(exact_script)

    # voice_id = "Amy|Ruth|Matthew"
    output_audio_path = output_location_path / f"{output_name}.mp3"
    synthesize_speech(
        exact_script, engine=engine, voice_id=voice, output_file=output_audio_path, polly_client=polly_client
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
