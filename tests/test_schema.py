# Third Party
import pytest

# Our Libraries
from very_demure.schema import SpeechSynthConfig


def test_invalid_voice():
    with pytest.raises(ValueError) as e_info:
        SpeechSynthConfig(voice="Darren")

    assert e_info.value.args[0] == "Unfortunately Darren is not one of ['Matthew', 'Amy', 'Ruth']."


def test_valid_voice():
    ss_conf = SpeechSynthConfig(voice="Amy")
    assert ss_conf.voice == "Amy"
