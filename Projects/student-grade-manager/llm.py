"""Small, swappable connection to a language model.

The rest of the app only calls `complete(system, user)` and gets text
back, so the model behind it can change without touching anything else.

Choose one with environment variables (or a .env file):
    LLM_PROVIDER=off      no AI at all (the default)
    LLM_PROVIDER=ollama   a free model running on this computer
    LLM_PROVIDER=openai   any OpenAI-compatible API (needs LLM_API_KEY)

Same module as in the log analyzer project, so both apps switch models
the same way.
"""
import json
import os
import urllib.error
import urllib.request


class LLMError(Exception):
    """The model could not be reached or gave an unusable reply."""


def post_json(url, payload, headers=None, timeout=60):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LLMError(f"could not reach the model: {error}") from error


class OllamaProvider:
    """A model served by Ollama (https://ollama.com) on this machine."""

    def __init__(self, model="llama3.2", url="http://localhost:11434"):
        self.model = model
        self.url = url.rstrip("/")

    def complete(self, system, user):
        reply = post_json(f"{self.url}/api/chat", {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "format": "json",   # ask Ollama for JSON only
            "stream": False,
            "options": {"temperature": 0},
        })

        try:
            return reply["message"]["content"]
        except (KeyError, TypeError) as error:
            raise LLMError(f"unexpected reply from Ollama: {reply!r}") from error


class OpenAICompatibleProvider:
    """Any service that speaks the OpenAI chat-completions format."""

    def __init__(self, api_key, model="gpt-4o-mini",
                 base_url="https://api.openai.com/v1"):
        if not api_key:
            raise LLMError("LLM_API_KEY is not set")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, system, user):
        reply = post_json(
            f"{self.base_url}/chat/completions",
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0,
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        try:
            return reply["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMError(f"unexpected reply from the API: {reply!r}") from error


def get_llm():
    """Build the provider chosen in the environment, or None when AI is off."""
    provider = os.getenv("LLM_PROVIDER", "off").strip().lower()

    if provider in ("", "off", "none"):
        return None

    if provider == "ollama":
        return OllamaProvider(
            model=os.getenv("LLM_MODEL", "llama3.2"),
            url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        )

    if provider == "openai":
        return OpenAICompatibleProvider(
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        )

    raise LLMError(f"unknown LLM_PROVIDER: {provider!r}")
