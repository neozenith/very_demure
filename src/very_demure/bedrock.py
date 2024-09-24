# Standard Library
import json
import logging
from typing import Any

# Third Party
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

logger = logging.getLogger(__name__)

MODEL_DEFAULT_CONFIG = {
    "amazon.titan-text-premier-v1:0": {
        "maxTokenCount": 512,
        "temperature": 0.5,
    },
    "meta.llama3-8b-instruct-v1:0": {},
    "meta.llama2-13b-chat-v1": {},
    "mistral.mistral-large-2402-v1:0": {},
    "stability.stable-diffusion-xl-v1": {},
}


def generate_mindfulness_script(
    client: BedrockRuntimeClient,
    duration: str = "10",
    model: str = "amazon.titan-text-premier-v1:0",
    engine: str = "neural",
    config: dict[str, Any] = None,
) -> Any:
    """Generate a guided mindfulness meditation using an Amazon bedrock Foundation Model."""
    textConfig = config if config else MODEL_DEFAULT_CONFIG[model]

    generative_voice_engine_caveat = """
        Be sure to use a <prosody rate="slow"> SSML tag around the whole text but inside the <speak> SSML tags.
    """
    if engine == "generative":
        generative_voice_engine_caveat = """
            Do not include <voice> or <prsody> SSML tags as they are not yet supported by the generative voices.
        """

    prompt = f"""
        You are a helpful assistant.

        Write the text for a guided mindfulness meditation session which should last {duration} minutes.
        This output script is being passed into AWS Polly to be synthesised into speech.
        
        Also please understand and use SSML speech markers to give the speech a slow and gentle voice.
        Insert the appropriate markers to actually add silent pauses where needed using these:
        https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html

        There should be some pauses that last longer than 30 seconds and some that are longer than a minute.
        However the maximum duration on any <break> SSML tag is 10 seconds. 
        You may need to add 3 <break time="10s" /> tags to create a 30 second pause.
        Do not do this:
        <break time="3x10s" />

        Instead do this:
        <break time="10s" /><break time="10s" /><break time="10s" />

        {generative_voice_engine_caveat}

        The start of script and end of script markers should be '[SCRIPT]' 
        but still include the SSML <speak> markers inside them.
    """

    native_request = {
        "inputText": prompt,
        "textGenerationConfig": textConfig,
    }

    logger.info(native_request)

    response = client.invoke_model(
        body=json.dumps(native_request),
        contentType="application/json",
        accept="application/json",
        modelId=model,
        trace="DISABLED",  # 'ENABLED'|'DISABLED'
    )
    logger.info(response)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["results"][0]["outputText"]
    logger.info(response_text)
    response_text = response_text.split("[SCRIPT]")[1]
    logger.info(response_text)
    return response_text
