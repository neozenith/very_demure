# Standard Library
import logging
import re
from pathlib import Path

# Third Party
import boto3
from ssml_builder.core import Speech

# Our Libraries
from very_demure.schema import DEFAULT_SPEECH_CONFIG, SpeechSynthConfig

logger = logging.getLogger(__name__)


def synthesize_speech(
    ssml_text: str,
    speech_synth_config: SpeechSynthConfig = DEFAULT_SPEECH_CONFIG,
    output_file: Path = Path("output.mp3"),
    polly_client=None,
):
    """Use AWS Polly Text to Speech Service to synthesize mp3 of the guided mindfulness audio."""
    # Create a Polly client
    if not polly_client:
        polly_client = boto3.client("polly", region_name="us-east-1")

    # Call the synthesize_speech API
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/synthesize_speech.html
    response = polly_client.synthesize_speech(
        Engine=speech_synth_config.engine,
        VoiceId=speech_synth_config.voice,
        Text=ssml_text,
        TextType="ssml",
        OutputFormat="mp3",
        SampleRate="24000",
    )

    # Save the audio stream returned by Amazon Polly on a file
    with output_file.open("wb") as file:
        file.write(response["AudioStream"].read())

    return output_file


def process_text_to_ssml(script: str, speech_synth_config: SpeechSynthConfig = DEFAULT_SPEECH_CONFIG) -> str:
    speech = Speech()
    logger.info(script)
    sanitised_script = process_pause_markers(script)
    speech.prosody(value=sanitised_script, rate=speech_synth_config.voice_speed)

    return speech.speak()


def process_pause_markers(script):
    """Process multiple pause markers in a longer multiline script."""
    pattern = re.compile("\\[PAUSE (\\d+)(m|s)\\]", re.IGNORECASE)
    output = re.sub(pattern, process_pause_marker_match, script)
    return output


def process_pause_marker_match(pause_marker_match: re.Match):
    """Take the regex Match and process the string."""
    return process_pause_marker(pause_marker_match.group(0))


def process_pause_marker(pause_marker):
    pattern = re.compile("\\[PAUSE (\\d+)(m|s)\\]", re.IGNORECASE)
    time_component = pattern.search(pause_marker)

    break_marker = '<break time="10s" />'

    if time_component:
        numeric, unit = time_component.group(1, 2)
        multiplier = 60 if unit.lower() == "m" else 1
        total_seconds = int(numeric) * multiplier
        increments = int(total_seconds / 10)
        output = break_marker * increments
    else:
        output = break_marker  # if in doubt just insert one valid one

    return output
