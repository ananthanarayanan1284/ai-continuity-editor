"""Where the project keeps its data files."""

from pathlib import Path

from continuity_editor.config import PROJECT_ROOT

DATA_DIR = PROJECT_ROOT / "data"


def raw_text_path(novel_id: str) -> Path:
    return DATA_DIR / "raw" / f"{novel_id}.txt"


def chapters_path(novel_id: str) -> Path:
    return DATA_DIR / "processed" / novel_id / "chapters.json"


def extraction_cache_dir() -> Path:
    """Saved chapter extractions, named by a fingerprint of the chapter text, so a chapter that
    appears unchanged in another version of the book (e.g. the test corpus) is not redone."""
    return DATA_DIR / "processed" / "extraction_cache"


def results_dir() -> Path:
    return DATA_DIR / "results"
