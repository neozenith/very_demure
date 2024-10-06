# Standard Library
import logging

# Our Libraries
from very_demure.schema import SpeechSynthConfig

logger = logging.getLogger(__name__)


def generate_prompt(speech_synth_config: SpeechSynthConfig) -> str:
    """Generate the LLM Prompt given the SpeechSynth input constraints and requests."""
    generative_voice_engine_caveat = get_generative_voice_engine_caveat(speech_synth_config)

    prompt = f"""
        Write the text for a guided mindfulness meditation session which should last 
        {speech_synth_config.duration_minutes} minutes. Do not mention this duration in the actual script.

        There should be some pauses that last longer than 30 seconds and some that are longer than a minute. 
        Indicate these pauses like this:
        [PAUSE 20s]

        The generated script should also include affirmations.
        
        {generative_voice_engine_caveat}
        The start of script and end of script markers should be '[SCRIPT]' 
        
    """

    logger.info(prompt)

    return prompt


def get_generative_voice_engine_caveat(speech_synth_config: SpeechSynthConfig) -> str:
    generative_voice_engine_caveat = """
        Be sure to use a SSML prosody tag with the literal value <prosody rate="{speech_synth_config.voice_speed}"> 
        SSML tag around the whole text but inside the <speak> SSML tags.
        Do not do this:
        <prosody rate="0.75x">
    """
    # if speech_synth_config.engine == "generative":

    generative_voice_engine_caveat = """
            Do not include <voice> or <prsody> SSML tags as they are not yet supported by the generative voices.
        """

    return generative_voice_engine_caveat
