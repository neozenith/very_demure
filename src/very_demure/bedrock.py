# Standard Library
import json
import logging
from typing import Any

# Third Party
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

# Our Libraries
from very_demure.prompt import generate_prompt
from very_demure.schema import SpeechSynthConfig

logger = logging.getLogger(__name__)
DEFAULT_SPEECH_CONFIG = SpeechSynthConfig(duration_minutes="10")
# https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/bedrock-runtime/models
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
    model: str = "amazon.titan-text-premier-v1:0",
    speech_synth_config: SpeechSynthConfig = DEFAULT_SPEECH_CONFIG,
    config: dict[str, Any] = None,
) -> Any:
    """Generate a guided mindfulness meditation using an Amazon Bedrock Foundation Model."""
    textConfig = config if config else MODEL_DEFAULT_CONFIG[model]

    prompt = generate_prompt(speech_synth_config)

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
