import re

import httpx

from app.core.config import settings

SYSTEM_PROMPT = (
    "You are a product-manual assistant. Answer the QUESTION using only the "
    "MANUAL EXCERPTS provided by the user.\n\n"
    "Formatting rules:\n"
    "- Write a clear, direct answer a rider can follow.\n"
    "- Use short paragraphs, or a numbered list for procedures.\n"
    "- Do not mention excerpts, context, sources, prompts, or that you are an AI.\n"
    "- Do not write phrases like 'Excerpt 1', 'according to the excerpt', "
    "or 'these steps are mentioned'.\n"
    "- Do not invent steps that are not in the excerpts.\n"
    "- Do not add notes telling the user to consult the manual; you are "
    "already answering from the manual.\n"
    "- Only reply with exactly 'I do not know.' when the excerpts contain "
    "nothing related to the question."
)

RETRY_SYSTEM_PROMPT = (
    "Answer the question using the manual text only.\n"
    "Use a clean numbered list for steps, or short paragraphs otherwise.\n"
    "Do not mention excerpts or context. Do not apologize. Do not say you "
    "do not know. Give concrete details from the text."
)

_UNHELPFUL_RE = re.compile(
    r"^\s*(i (do not|don't|cannot|can't) know"
    r"|i('m| am) (not sure|unable)"
    r"|no (relevant )?information"
    r"|not (enough|sufficient) (information|context)"
    r"|the (provided )?(context|excerpts?) (do not|don't|does not|doesn't)"
    r").*$",
    re.IGNORECASE | re.DOTALL,
)

_EXCERPT_CITE_RE = re.compile(
    r"\s*\(?\s*Excerpt\s+\d+\s*\)?",
    re.IGNORECASE,
)
_META_TRAILER_RE = re.compile(
    r"\n+\s*(These steps are mentioned.*?|According to the excerpt.*?|"
    r"As mentioned in the excerpt.*?|The (manual )?excerpts? (say|state).*?|"
    r"Note:\s*It is recommended to consult.*?|"
    r"Please (refer to|consult) the (user )?manual.*?)"
    r"\s*$",
    re.IGNORECASE | re.DOTALL,
)


class OllamaChatError(Exception):
    pass


def build_user_prompt(query: str, context_chunks: list[str]) -> str:
    if not context_chunks:
        excerpts = "(none)"
    else:
        excerpts = "\n\n".join(context_chunks)

    return (
        "=== MANUAL EXCERPTS ===\n"
        f"{excerpts}\n"
        "=== END EXCERPTS ===\n\n"
        f"QUESTION: {query}\n\n"
        "Write the final user-facing answer now. Follow the formatting rules."
    )


def is_unhelpful_answer(answer: str) -> bool:
    cleaned = answer.strip()
    if not cleaned:
        return True
    if len(cleaned) <= 120 and _UNHELPFUL_RE.match(cleaned):
        return True
    lowered = cleaned.lower()
    refusal_stubs = (
        "i do not know",
        "i don't know",
        "i cannot answer",
        "i can't answer",
    )
    return any(lowered == stub or lowered == f"{stub}." for stub in refusal_stubs)


def format_answer(answer: str) -> str:
    cleaned = answer.strip()
    cleaned = _EXCERPT_CITE_RE.sub("", cleaned)
    cleaned = _META_TRAILER_RE.sub("", cleaned)
    # Tiny models sometimes append a refusal after a valid answer.
    cleaned = re.sub(
        r"\n+\s*i (do not|don't) know\.?\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    return cleaned.strip()


def fallback_answer_from_context(context_chunks: list[str]) -> str:
    body = "\n\n".join(context_chunks)
    return format_answer(
        "Here is what the manual says that relates to your question:\n\n"
        f"{body}",
    )


async def _chat(
    *,
    system: str,
    user: str,
    temperature: float,
) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_chat_model,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 512,
        },
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
    except httpx.HTTPError as exc:
        raise OllamaChatError(f"Ollama chat request failed: {exc}") from exc

    if response.status_code != 200:
        raise OllamaChatError(
            f"Ollama chat failed ({response.status_code}): {response.text}",
        )

    data = response.json()
    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        raise OllamaChatError("Ollama chat response missing message content")

    return str(content).strip()


async def generate_answer(*, query: str, context_chunks: list[str]) -> str:
    user_prompt = build_user_prompt(query, context_chunks)
    answer = await _chat(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=0.2,
    )
    answer = format_answer(answer)

    if not is_unhelpful_answer(answer):
        return answer

    retry_answer = format_answer(
        await _chat(
            system=RETRY_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.1,
        ),
    )
    if not is_unhelpful_answer(retry_answer):
        return retry_answer

    return fallback_answer_from_context(context_chunks)
