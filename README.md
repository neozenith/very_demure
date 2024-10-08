# Very Demure, Very Mindful

<div align="center">
    <img src="docs/assets/logo3.webp" width="200px" />
    <img src="docs/assets/logo4.webp" width="200px" />
    <p><i>Logo(s) generated by DALL-E and ChatGPT-4o</i></p>
</div>
The name is a play on a current TikTok trend.

# Motivation

After listening to this [podcast](https://brenebrown.com/podcast/finding-focus-and-owning-your-attention/) 
where Brené Brown interviews Dr Amishi Jha to dive into the distinction between _Focus_, _Attention_ and _Memory_, 
I have a renewed interest in my own mindfulness practices.

Dr. Gabor Mate writes in his book [Scattered Minds](https://drgabormate.com/book/scattered-minds/) about the importance 
of a mindfulness practice to help those with ADHD to manage and even reverse some of the attention deficit traits.

After trying a few different "mindfulness" apps, I wasn't convinced of their value with subscription pricing 
but could I have a more on-demand model? _**Turns out, yes I can.**_

# Architecture

<details>
    <summary><i>Click this arrow for detailed diagram</i>
        <h4>Architecture Diagram: Simple</h4>
        <img src="infra/docs/diagrams/diagram-simple.png" alt="Architecture Diagram: Simple" width="50%" />
    </summary>
    <h4>Architecture Diagram: Detailed</h4>
    <img src="infra/docs/diagrams/diagram-detailed.png" alt="Architecture Diagram: Detailed" width="50%" />
</details>

# Roadmap

## Done

- get OpenAI to generate a guided mindfulness transcript
- get AWS Polly to use the text-to-speech to synthesize the audio.
- Add slower cadence and pauses. Leverage [SSML](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html)
- Add AWS Bedrock intregration to leverage their models
- Deploy to CloudFront with security best practices (OAC)
- Deploy under custom domain name with SSL Certificate.

## TODO

- Port simple HTML/CSS to React SPA
- Add Lambda@Edge and Cognito authenticated areas (Google SSO as MVP)
- Add API Gateway + Lambda API endpoint
    - Simple HelloWorld
    - List user protected content
    - Allow user to generate new content
- Consolidate the API Gateway Endpoint and the CloudFront static site under the same url but use Lambda@Edge to redirect /api/ requests to API Gateway instead
- Integrate Stripe or some other payment portal provider to make generating on-demand new audio tracks as a pay-per-generate option.


# Quickstart

```sh
make dev

# Generate script for a "10 minute" session.
# TODO: Get the generated audio to actually pause with silence when cued.
python3 -m very_demure --duration 10 --voice Matthew

python3 -m http.server --directory docs
```

# Samples

Checkout an example transcript and MP3 in the [`docs/samples/`](docs/samples/) folder

