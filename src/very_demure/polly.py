# Standard Library
from pathlib import Path

# Third Party
import boto3


def synthesize_speech(
    text, output_format="mp3", engine="generative", voice_id="Joanna", output_file="output.mp3", polly_client=None
):
    # Create a Polly client
    if not polly_client:
        polly_client = boto3.client("polly", region_name="us-east-1")

    # Call the synthesize_speech API
    response = polly_client.synthesize_speech(Engine=engine, Text=text, OutputFormat=output_format, VoiceId=voice_id)

    # Save the audio stream returned by Amazon Polly on a file
    with Path(output_file).open("wb") as file:
        file.write(response["AudioStream"].read())

    print(f"Speech synthesized and saved to {output_file}")
