# Third Party
from openai import OpenAI


def generate_mindfulness_script(client: OpenAI, duration: str = "1"):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""
                Write the text for a guided mindfulness meditation session which should last {duration} minute.
                This output script is being passed into AWS Polly to be synthesised into speech.
                The start of script and end of script markers shold be '[SCRIPT]'
                """,
            },
        ],
    )

    return completion.choices[0].message
