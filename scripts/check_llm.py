"""Check the local LLM: Ollama is running, the model is downloaded, and it returns a
structured answer. The first answer is slower because the model is loaded into memory.

    python scripts/check_llm.py
"""

import time

from pydantic import BaseModel

from continuity_editor.llm import LLMClient

PASSAGE = (
    "Mira looked up, her blue eyes sharp in the lamplight. "
    "At twenty-five, she was the youngest captain in the fleet."
)


class CharacterFacts(BaseModel):
    name: str
    eye_colour: str | None
    age: int | None


def main() -> None:
    llm = LLMClient()
    info = llm.verify()
    print(f"Ollama is running. Model: {info['model']} ({info['parameters']}, {info['quantization']})")

    start = time.perf_counter()
    facts = llm.structured(
        f"Extract the facts stated about the character in this passage.\n\n{PASSAGE}", CharacterFacts
    )
    print(f"Answer in {time.perf_counter() - start:.1f}s: {facts.model_dump()}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(f"Error: {exc}")
