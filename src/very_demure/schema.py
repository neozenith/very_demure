# Standard Library
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

VALID_VOICES = ["Matthew", "Amy", "Ruth"]


@dataclass
class SpeechSynthConfig:
    engine: str = "neural"
    voice: str = "Matthew"
    voice_speed: str = "slow"
    duration_minutes: str = "1"

    def __post_init__(self):
        if self.voice not in VALID_VOICES:
            raise ValueError(f"Unfortunately {self.voice} is not one of {VALID_VOICES}.")


DEFAULT_SPEECH_CONFIG = SpeechSynthConfig()


@dataclass
class LLMProviderConfig:
    provider: str
    model_id: str
