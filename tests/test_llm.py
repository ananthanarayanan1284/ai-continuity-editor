"""Ollama tests. The live one needs Ollama running with the model downloaded; it is skipped otherwise."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from continuity_editor.config import LLMSettings
from continuity_editor.llm import LLMClient


class EyeColour(BaseModel):
    character: str
    eye_colour: str


def test_unreachable_server_gives_a_clear_error():
    llm = LLMClient(LLMSettings(ollama_host="http://127.0.0.1:9", _env_file=None))
    with pytest.raises(RuntimeError, match="ollama.com/download"):
        llm.verify()


def test_a_cached_answer_is_reused_without_asking_the_model(tmp_path):
    class FakeOllama:
        calls = 0

        def chat(self, **request):
            FakeOllama.calls += 1
            message = SimpleNamespace(content='{"character": "Mira", "eye_colour": "blue"}')
            return SimpleNamespace(message=message, prompt_eval_count=10, eval_count=5, total_duration=1)

    llm = LLMClient(LLMSettings(_env_file=None), cache_dir=tmp_path)
    llm._client = FakeOllama()
    first = llm.structured("Which character?", EyeColour)
    again = llm.structured("Which character?", EyeColour)
    assert first == again == EyeColour(character="Mira", eye_colour="blue")
    assert FakeOllama.calls == 1
    assert llm.usage["calls"] == 1


@pytest.fixture(scope="module")
def llm():
    client = LLMClient()
    try:
        client.verify()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    return client


@pytest.mark.integration
def test_structured_answer_matches_schema(llm):
    answer = llm.structured(
        "Mira looked up, her blue eyes sharp in the lamplight.\n\n"
        "Which character is described, and what colour are their eyes?",
        EyeColour,
    )
    assert answer.character.startswith("Mira")
    assert answer.eye_colour.lower() == "blue"
