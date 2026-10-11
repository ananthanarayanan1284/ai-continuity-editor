"""Local LLM access through Ollama: free, runs on this computer, no account or API key.

Every call asks for JSON matching a Pydantic model. Ollama constrains the output to that
model's JSON schema, so callers get validated objects back instead of raw text.
"""

import hashlib
import json
from pathlib import Path
from typing import TypeVar

from ollama import Client, ResponseError
from pydantic import BaseModel

from continuity_editor.config import LLMSettings, get_llm_settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Usage:
        llm = LLMClient()
        llm.verify()
        answer = llm.structured("Which character ... ?", MySchema)
    """

    def __init__(self, settings: LLMSettings | None = None, cache_dir: Path | None = None) -> None:
        self.settings = settings or get_llm_settings()
        self.model = self.settings.llm_model
        self._client = Client(host=self.settings.ollama_host)
        # With a cache_dir, each answer is saved under a hash of the full request, so re-running
        # an interrupted job reuses the answers instead of asking the (slow) model again.
        # Answers are repeatable (temperature 0), so a saved one is what the model would say.
        self.cache_dir = cache_dir
        # Running totals across calls, for reporting speed and cost of a run.
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "seconds": 0.0}

    def verify(self) -> dict[str, str]:
        """Check that Ollama is running and the model is downloaded, and return model details."""
        try:
            info = self._client.show(self.model)
        except ConnectionError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {self.settings.ollama_host}. Install it from "
                "https://ollama.com/download and make sure the Ollama app is running."
            ) from exc
        except ResponseError as exc:
            if exc.status_code == 404:
                raise RuntimeError(
                    f"The model {self.model!r} is not downloaded yet. Run: ollama pull {self.model}"
                ) from exc
            raise
        details = info.details
        return {
            "model": self.model,
            "parameters": (details and details.parameter_size) or "unknown",
            "quantization": (details and details.quantization_level) or "unknown",
        }

    def structured(
        self, prompt: str, schema: type[T], system: str | None = None, max_tokens: int | None = None
    ) -> T:
        """Ask the model and parse its answer into `schema`.

        Temperature 0 keeps answers repeatable, which the evaluation relies on. `max_tokens`
        caps the answer length; an answer cut off by it fails validation (pydantic.ValidationError).
        """
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        options = {"temperature": 0, "num_ctx": self.settings.llm_context_tokens}
        if max_tokens:
            options["num_predict"] = max_tokens
        extra = {} if self.settings.llm_think is None else {"think": self.settings.llm_think}
        cached = None
        if self.cache_dir:
            request = [self.model, messages, schema.model_json_schema(), options, extra]
            key = hashlib.sha256(json.dumps(request, sort_keys=True).encode("utf-8")).hexdigest()
            cached = self.cache_dir / f"{key}.json"
            if cached.exists():
                return schema.model_validate_json(cached.read_text(encoding="utf-8"))
        response = self._client.chat(
            model=self.model,
            messages=messages,
            format=schema.model_json_schema(),
            options=options,
            **extra,
        )
        self.usage["calls"] += 1
        self.usage["input_tokens"] += response.prompt_eval_count or 0
        self.usage["output_tokens"] += response.eval_count or 0
        self.usage["seconds"] += (response.total_duration or 0) / 1e9
        answer = schema.model_validate_json(response.message.content)
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text(response.message.content, encoding="utf-8")
        return answer
