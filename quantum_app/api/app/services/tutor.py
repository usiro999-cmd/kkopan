from openai import AsyncAzureOpenAI

from app.config import Settings


class AIConfigurationError(RuntimeError):
    pass


SYSTEM_PROMPT = """
You are a graduate-level teaching assistant for an educational quantum
machine-learning drug-discovery simulation. Explain Qiskit state fidelity,
RDKit descriptors, ranking statistics, and experimental design rigorously.
All candidates and labels are synthetic. Never provide diagnosis, treatment,
dosing, clinical recommendations, or claims that the simulation predicts
real efficacy or safety. Explicitly distinguish mathematical similarity from
biological evidence.
""".strip()


async def ask_tutor(
    question: str, screening_context: dict | None, settings: Settings
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
    context = (
        f"\nSynthetic screening context: {screening_context}"
        if screening_context
        else ""
    )
    response = await client.chat.completions.create(
        model=settings.azure_openai_deployment,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question + context},
        ],
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("Azure OpenAI returned an empty response")
    return answer
