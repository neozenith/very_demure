# Standard Library
import logging

# Third Party
from openai import OpenAI

# Our Libraries
from very_demure.prompt import generate_prompt
from very_demure.schema import DEFAULT_SPEECH_CONFIG, SpeechSynthConfig

logger = logging.getLogger(__name__)


def generate_mindfulness_script(
    client: OpenAI, model: str = "gpt-4o", speech_synth_config: SpeechSynthConfig = DEFAULT_SPEECH_CONFIG
) -> str:
    """Use the OpenAI models to generate a guided mindfulness script."""
    prompt = generate_prompt(speech_synth_config=speech_synth_config)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": prompt,
        },
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return completion.choices[0].message.content.split("[SCRIPT]")[1]
