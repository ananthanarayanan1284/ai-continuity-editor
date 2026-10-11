"""The test corpus: the book with deliberately injected contradictions, plus a few harmless
"control" edits that restate a fact and must not be flagged. The injections are listed in
data/test_corpus/<novel>_injections.json."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from continuity_editor.checking.checker import Confidence
from continuity_editor.extraction.chapters import ChapterText


class Injection(BaseModel):
    id: str
    kind: Literal["contradiction", "control"]
    chapter: int
    category: str | None = None
    expected_confidence: Confidence | None = None
    find: str  # original text, which must occur exactly once in the chapter
    replace: str  # the text put in its place
    contradicts_chapter: int | None = None
    contradicts: str | None = None  # the earlier sentence it contradicts
    note: str = ""


def load_injections(path: Path) -> list[Injection]:
    return [Injection.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def apply_injections(chapters: list[ChapterText], injections: list[Injection]) -> list[ChapterText]:
    """A copy of `chapters` with every injection applied."""
    texts = {c.number: c.text for c in chapters}
    for injection in injections:
        count = texts[injection.chapter].count(injection.find)
        if count != 1:
            raise ValueError(
                f"{injection.id}: the text to replace must occur once in chapter {injection.chapter}, "
                f"found {count} times: {injection.find!r}"
            )
        texts[injection.chapter] = texts[injection.chapter].replace(injection.find, injection.replace)
    return [ChapterText(c.number, c.title, texts[c.number]) for c in chapters]
