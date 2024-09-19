# Very Demure, Very Mindful

<!--TOC-->

- [Very Demure, Very Mindful](#very-demure-very-mindful)
- [Quickstart](#quickstart)

<!--TOC-->

The name is a play on a current TikTok trend,

The actual goal is to:
- get OpenAI to generate a guided mindfulness track
- get AWS Polly to use the text-to-speech to synthesize the audio.

# Quickstart

```sh
make dev

# Generate script for a "10 minute" session.
# TODO: Get the generated audio to actually pause with silence when cued.
python3 -m very_demure --duration 10

open output.mp3
```