"""Shared fixtures for tests that need a live service; they skip when it isn't available."""

import pytest

from continuity_editor.config import get_neo4j_settings
from continuity_editor.graph import Neo4jConnection, apply_schema
from continuity_editor.llm import LLMClient


@pytest.fixture(scope="session")
def neo4j_conn():
    try:
        settings = get_neo4j_settings()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    with Neo4jConnection(settings) as connection:
        apply_schema(connection)
        yield connection


@pytest.fixture(scope="session")
def live_llm():
    client = LLMClient()
    try:
        client.verify()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    return client


CONFIRMED = {"reason": "Same property, and both cannot be true.", "same_property": True, "both_can_be_true": False}


class FakeJudge:
    """Stands in for the LLM in checker tests: gives the same judgement every time (and, for
    the double-check, `verification`, by default a confirmed clash). Counts calls."""

    model = "fake"

    def __init__(self, answer, verification=CONFIRMED):
        self.answer = answer
        self.verification = verification
        self.calls = 0

    def structured(self, prompt, schema, system=None, max_tokens=None):
        self.calls += 1
        if schema.__name__ == "Verification":
            return schema.model_validate(self.verification)
        return schema.model_validate(self.answer)
