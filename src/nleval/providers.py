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


def ollama(model: str) -> Callable[[str], str]:
    """A locally-hosted model over Ollama's HTTP API.

    Present so the suite can be run for nothing at all. A Dutch benchmark whose
    only paths are paid APIs cannot be re-run by the people most likely to
    check it, and the whole no-judge design exists to keep a run cheap.
    """
    import json as _json
    import urllib.error
    import urllib.request

    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")

    def call(prompt: str) -> str:
        body = _json.dumps(
            {
                "model": model,
                "stream": False,
                "options": {"temperature": 0, "num_predict": 24},
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode()
        req = urllib.request.Request(
            f"{host}/api/chat", data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                payload = _json.loads(r.read())
        except urllib.error.URLError as e:
            raise ProviderError(
                f"cannot reach Ollama at {host} ({e}). Start it with `ollama serve` "
                f"and pull the model with `ollama pull {model}`."
            ) from e
        return (payload.get("message", {}).get("content") or "").strip()

    return call


def hf(model: str) -> Callable[[str], str]:
    """A local Hugging Face causal model, used for log-probability scoring.

    This exists for the minimal pairs. BLiMP-NL is designed to be scored by
    comparing the log-likelihood a model assigns to the grammatical and
    ungrammatical sentence, not by asking it to pick one: a forced choice can
    be right for the wrong reason, and it measures instruction-following as
    much as grammar. Chat APIs will not return the likelihood of text they did
    not generate, so the correct scoring needs a model whose weights are local.

    Returned callable answers prompts as usual; the `.score` attribute added
    below is what the runner uses for minimal pairs.
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:
        raise ProviderError(
            "the hf provider needs torch and transformers: pip install 'nl-eval[local]'"
        ) from e

    tok = AutoTokenizer.from_pretrained(model)
    mdl = AutoModelForCausalLM.from_pretrained(model)
    mdl.eval()

    @torch.no_grad()
    def score(sentences: list[str]) -> list[float]:
        """Mean per-token log-probability of each sentence.

        Mean rather than sum: the two sentences in a minimal pair can differ in
        token count, and a sum would systematically prefer the shorter one,
        which would score tokenisation rather than grammar.
        """
        out = []
        for text in sentences:
            ids = tok(text, return_tensors="pt")
            input_ids = ids["input_ids"]
            if input_ids.shape[1] < 2:
                out.append(float("-inf"))
                continue
            logits = mdl(**ids).logits
            logprobs = torch.log_softmax(logits[:, :-1], dim=-1)
            target = input_ids[:, 1:]
            picked = logprobs.gather(2, target.unsqueeze(-1)).squeeze(-1)
            out.append(float(picked.mean()))
        return out

    @torch.no_grad()
    def call(prompt: str) -> str:
        ids = tok(prompt, return_tensors="pt")
        gen = mdl.generate(**ids, max_new_tokens=8, do_sample=False,
                           pad_token_id=tok.eos_token_id)
        return tok.decode(gen[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    call.score = score  # type: ignore[attr-defined]
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
    "hf": hf,
    "ollama": ollama,
    "openai": openai,
    "anthropic": anthropic,
}


def get(provider: str, model: str) -> Callable[[str], str]:
    if provider not in REGISTRY:
        raise ProviderError(
            f"unknown provider {provider!r}; available: {', '.join(sorted(REGISTRY))}"
        )
    return REGISTRY[provider](model)
