"""Extract entities, facts and events from a prepared novel with the local LLM.

Each chapter's result is saved, so re-running only processes chapters that aren't done yet.

    python scripts/extract_novel.py                      # every chapter of oz
    python scripts/extract_novel.py --chapters 1 2 3
"""

import argparse

from continuity_editor.extraction import extract_novel, load_chapters
from continuity_editor.llm import LLMClient
from continuity_editor.paths import chapters_path, extraction_cache_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract facts from a prepared novel.")
    parser.add_argument("--novel-id", default="oz")
    parser.add_argument("--chapters", type=int, nargs="*", help="chapter numbers (default: all)")
    parser.add_argument("--force", action="store_true", help="redo chapters that were already extracted")
    args = parser.parse_args()

    path = chapters_path(args.novel_id)
    if not path.exists():
        raise SystemExit(f"{path} not found. Run scripts/prepare_novel.py first.")
    chapters = load_chapters(path)
    if args.chapters:
        chapters = [c for c in chapters if c.number in set(args.chapters)]

    llm = LLMClient()
    llm.verify()
    results = extract_novel(llm, args.novel_id, chapters, extraction_cache_dir(), force=args.force)
    for r in results:
        print(
            f"ch{r.chapter_number:02d}  {len(r.entities):>3} entities  {len(r.facts):>3} facts  "
            f"{len(r.events):>3} events  {r.unverified_dropped:>2} dropped  {r.seconds:>5.0f}s  {r.chapter_title}"
        )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(f"Error: {exc}")
