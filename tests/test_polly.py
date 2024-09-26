# Standard Library
import logging
from pathlib import Path

# Third Party
import pytest

# Our Libraries
from very_demure.polly import (
    process_pause_marker,
    process_pause_markers,
    process_text_to_ssml,
)
from very_demure.schema import SpeechSynthConfig

logger = logging.getLogger(__name__)

TEST_SCRIPTS_PATH = Path("tests/test_polly_scripts")

test_scenarios = dict(
    {
        f.name: (f.read_text(), (f.parent / f.name.replace("-test.txt", "-expectation.ssml.xml")).read_text())
        for f in TEST_SCRIPTS_PATH.glob("*-test.txt")
    }
)


@pytest.mark.parametrize("test_case,expectation", test_scenarios.values(), ids=test_scenarios.keys())
def test_valid_ssml(test_case, expectation):
    # Given
    ss_conf = SpeechSynthConfig()

    # When
    result = process_text_to_ssml(test_case, speech_synth_config=ss_conf)

    # Then
    assert result == expectation


test_pause_marker_scenarios = {
    "20-seconds": ("[PAUSE 20s]", '<break time="10s" />' * 2),
    "1-minute": ("[PAUSE 1m]", '<break time="10s" />' * 6),
}


@pytest.mark.parametrize(
    "test_case,expectation", test_pause_marker_scenarios.values(), ids=test_pause_marker_scenarios.keys()
)
def test_process_pause_marker(test_case, expectation):
    # Given

    # When
    result = process_pause_marker(test_case)

    # Then
    assert result == expectation


test_pause_markers_scenarios = {
    "single line": ("[PAUSE 20s][PAUSE 1m]", '<break time="10s" />' * 8),
    "multi-line": (
        "[PAUSE 20s]\nWelcome\n[PAUSE 1m]",
        '<break time="10s" />' * 2 + "\nWelcome\n" + '<break time="10s" />' * 6,
    ),
}


@pytest.mark.parametrize(
    "test_case,expectation", test_pause_markers_scenarios.values(), ids=test_pause_markers_scenarios.keys()
)
def test_process_pause_markers(test_case, expectation):
    # Given

    # When
    result = process_pause_markers(test_case)

    # Then
    assert result == expectation
