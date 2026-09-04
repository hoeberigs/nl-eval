"""Model adapters.

Kept deliberately thin. Adding a provider should mean writing one function, not
learning a framework, and no adapter is imported until it is actually selected
so the suite installs with no provider SDKs at all.
"""

from __future__ import annotations

import os
from typing import Callable

SYSTEM = (
    "Je bent een taalkundig nauwkeurige assistent. "
    "Antwoord altijd in het Nederlands en uitsluitend met wat er gevraagd wordt, "
    "zonder uitleg."
)


class ProviderError(RuntimeError):
    pass


def _need(var: str) -> str:
    val = os.environ.get(var)
    if not val:
        raise ProviderError(
            f"{var} is not set. Export a key for this provider, or use "
            "--provider echo to exercise the harness without spending anything."
        )
    return val


def echo(model: str) -> Callable[[str], str]:
    """A provider that answers nothing.

    Present so the whole pipeline, rendering, extraction, scoring and reporting,
    can be exercised end to end without an API key or a cent of spend. Its score
    should land at zero, which also proves the scorer is not handing out marks
    for free.
    """

    def call(prompt: str) -> str:
        return ""

    return call


def always(model: str) -> Callable[[str], str]:
    """Always answers "A": the position-bias control.

    If this scores meaningfully above the chance baseline, the answer key is
    unbalanced and the suite is measuring letter preference, not Dutch.
    """

    def call(prompt: str) -> str:
        return "A"

    return call


def openai(model: str) -> Callable[[str], str]:
    key = _need("OPENAI_API_KEY")
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ProviderError("pip install openai") from e
    client = OpenAI(api_key=key)

    def call(prompt: str) -> str:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=64,
        )
        return (r.choices[0].message.content or "").strip()

    return call


def anthropic(model: str) -> Callable[[str], str]:
    key = _need("ANTHROPIC_API_KEY")
    try:
        import anthropic as _a
    except ImportError as e:
        raise ProviderError("pip install anthropic") from e
    client = _a.Anthropic(api_key=key)

    def call(prompt: str) -> str:
        r = client.messages.create(
            model=model,
            system=SYSTEM,
            max_tokens=64,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()

    return call


REGISTRY = {
    "echo": echo,
    "always-a": always,
    "openai": openai,
    "anthropic": anthropic,
}


def get(provider: str, model: str) -> Callable[[str], str]:
    if provider not in REGISTRY:
        raise ProviderError(
            f"unknown provider {provider!r}; available: {', '.join(sorted(REGISTRY))}"
        )
    return REGISTRY[provider](model)
