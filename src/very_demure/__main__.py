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
from very_demure.polly import process_text_to_ssml, synthesize_speech
from very_demure.schema import LLMProviderConfig, SpeechSynthConfig
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

    # Consume configuration
    llm_config = LLMProviderConfig(
        provider=cli_args.get("provider", "bedrock"), model_id=cli_args.get("model", "amazon.titan-text-premier-v1:0")
    )

    ss_conf = SpeechSynthConfig(
        engine=cli_args.get("engine", "neural"),
        voice=cli_args.get("voice", "Matthew"),  # voice_id = "Amy|Ruth|Matthew"
        voice_speed=cli_args.get("speed", "x-slow"),
        duration_minutes=cli_args.get("duration", "1"),
    )

    # Prepare file outputs
    model_name = sanitise_model_name(llm_config.model_id)
    script_output_name = f"{llm_config.provider}-{model_name}-{ss_conf.engine}-{ss_conf.duration_minutes}"
    audio_output_name = (
        f"{llm_config.provider}-{model_name}-{ss_conf.engine}-{ss_conf.duration_minutes}-{ss_conf.voice}"
    )

    output_location = cli_args.get("output_location", "./dist/assets/")
    output_location_path = Path(output_location)
    logger.info(output_location_path)
    output_location_path.parent.mkdir(parents=True, exist_ok=True)

    # Setup API Clients. See `.env.sample` for assumed environment variables for credentials
    openai_client = OpenAI()
    boto3_session = boto3.Session()
    polly_client = boto3_session.client("polly", region_name="us-east-1")
    bedrock_runtime_client: BedrockRuntimeClient = boto3_session.client("bedrock-runtime", region_name="us-east-1")
    logger.info("Clients created...")

    # Generate Script
    if llm_config.provider == "openai":
        script = openai_generate_mindfulness_script(client=openai_client, speech_synth_config=ss_conf)

    elif llm_config.provider == "bedrock":
        script = bedrock_generate_mindfulness_script(
            client=bedrock_runtime_client, model=llm_config.model_id, speech_synth_config=ss_conf
        )

    exact_ssml_script = process_text_to_ssml(script).replace('pitch="medium" volume="medium"', "")
    logger.info(exact_ssml_script)

    # Save a copy of the transcript
    transcript_file = output_location_path / f"{script_output_name}.ssml.xml"
    transcript_file.write_text(exact_ssml_script)

    # Synth all voices
    for voice in ["Amy", "Matthew", "Ruth"]:
        audio_output_name = f"{llm_config.provider}-{model_name}-{ss_conf.engine}-{ss_conf.duration_minutes}-{voice}"
        output_audio_path = output_location_path / f"{audio_output_name}.mp3"
        ss_conf.voice = voice
        synthesize_speech(
            exact_ssml_script, speech_synth_config=ss_conf, output_file=output_audio_path, polly_client=polly_client
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
