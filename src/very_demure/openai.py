# Standard Library
import logging

# Third Party
from openai import OpenAI

logger = logging.getLogger(__name__)


def generate_mindfulness_script(client: OpenAI, duration: str = "10", model="gpt-4o", engine="neural"):
    generative_voice_engine_caveat = """
        Be sure to use a <prosody rate="slow"> SSML tag around the whole text but inside the <speak> SSML tags.
    """
    if engine == "generative":
        generative_voice_engine_caveat = """
            Do not include <voice> or <prsody> SSML tags as they are not yet supported by the generative voices.
        """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"""
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
                """,
        },
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return completion.choices[0].message
