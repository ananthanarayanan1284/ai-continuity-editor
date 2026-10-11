"""Turn a book's raw text into chapters, and chapters into chunks the LLM can read."""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

_GUTENBERG_START = re.compile(r"^\*\*\* START OF .*$", re.MULTILINE)
_GUTENBERG_END = re.compile(r"^\*\*\* END OF .*$", re.MULTILINE)
# "Chapter I", "CHAPTER 12.", "Chapter IV. The Road" (a strict Roman numeral or a number)
_HEADING = re.compile(
    r"^[ \t]*chapter[ \t]+(\d+|(?=[mdclxvi])m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3}))\b\.?[ \t]*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)
_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


@dataclass
class ChapterText:
    number: int
    title: str
    text: str  # paragraphs separated by blank lines, each paragraph on one line

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def strip_gutenberg(text: str) -> str:
    """Drop the Project Gutenberg header and licence footer, if present."""
    text = text.replace("\r\n", "\n")
    start = _GUTENBERG_START.search(text)
    end = _GUTENBERG_END.search(text)
    return text[start.end() if start else 0 : end.start() if end else len(text)]


def split_chapters(text: str) -> list[ChapterText]:
    """Split a book on headings such as "Chapter I" or "CHAPTER 12. Title".

    The title may follow the number on the same line or sit on the next line. A table of
    contents repeats the headings, so when a chapter number appears more than once, the
    last occurrence (the real chapter) wins.
    """
    text = text.replace("\r\n", "\n")
    matches = list(_HEADING.finditer(text))
    chapters: dict[int, ChapterText] = {}
    for match, following in zip(matches, [*matches[1:], None]):
        title = match.group(2).strip()
        body = text[match.end() : following.start() if following else len(text)]
        if not title:
            title, body = _title_from_next_line(body)
        number = _to_int(match.group(1))
        chapters[number] = ChapterText(number, title, _unwrap(body))
    return [chapters[number] for number in sorted(chapters)]


def chunk_text(text: str, max_words: int = 900) -> list[str]:
    """Group paragraphs into chunks of at most `max_words` words. A longer paragraph stays whole."""
    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for paragraph in text.split("\n\n"):
        words = len(paragraph.split())
        if current and count + words > max_words:
            chunks.append("\n\n".join(current))
            current, count = [], 0
        current.append(paragraph)
        count += words
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def save_chapters(chapters: list[ChapterText], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(c) for c in chapters], ensure_ascii=False, indent=1), encoding="utf-8")


def load_chapters(path: Path) -> list[ChapterText]:
    return [ChapterText(**item) for item in json.loads(path.read_text(encoding="utf-8"))]


def _title_from_next_line(body: str) -> tuple[str, str]:
    """Use the first line after the heading as the title if it is short and stands alone."""
    first, _, rest = body.lstrip("\n").partition("\n")
    if first.strip() and len(first) <= 80 and rest.startswith("\n"):
        return first.strip(), rest
    return "", body


def _unwrap(body: str) -> str:
    """Join hard-wrapped lines so each paragraph is one line; keep blank lines between paragraphs."""
    paragraphs = (" ".join(line.strip() for line in block.splitlines()) for block in re.split(r"\n\s*\n", body))
    return "\n\n".join(p for p in paragraphs if p)


def _to_int(numeral: str) -> int:
    if numeral.isdigit():
        return int(numeral)
    values = [_ROMAN[c] for c in numeral.lower()]
    return sum(-v if v < nxt else v for v, nxt in zip(values, [*values[1:], 0]))
