from openai import AsyncAzureOpenAI

from app.config import Settings
from app.services.tutor import AIConfigurationError


SYSTEM_PROMPT = """
You are a graduate-level fusion-energy research assistant. Explain plasma
physics, magnetic confinement, Lawson criterion, transport, MHD stability,
diagnostics, uncertainty, and experimental design rigorously. Treat supplied
scenario values as outputs of a simplified zero-dimensional educational model.
Never present them as reactor validation or operational guidance. Do not provide
instructions for handling tritium, high voltage, cryogens, radiation sources,
vacuum hardware, or facility controls. When a question touches experimental
operations, direct the user to their institution's approved procedures and
qualified safety personnel. Clearly separate model inference from measured
evidence and identify important missing physics.
""".strip()


async def ask_fusion_assistant(
    question: str, scenario: dict | None, settings: Settings
) -> str:
    required = (
        settings.azure_openai_endpoint,
        settings.azure_openai_api_key,
        settings.azure_openai_deployment,
    )
    if not all(required):
        raise AIConfigurationError(
            "Azure OpenAI is not configured. Set endpoint, key, and deployment."
        )
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )
    context = f"\nEducational scenario: {scenario}" if scenario else ""
    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        temperature=0.15,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question + context},
        ],
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("Azure OpenAI returned an empty response")
    return answer
