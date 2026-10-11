"""Download a Project Gutenberg book, remove the licence text, and split it into chapters.

    python scripts/prepare_novel.py                                        # The Wonderful Wizard of Oz
    python scripts/prepare_novel.py --gutenberg-id 2852 --novel-id baskervilles
"""

import argparse
import urllib.request

from continuity_editor.extraction import save_chapters, split_chapters, strip_gutenberg
from continuity_editor.paths import chapters_path, raw_text_path

GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and split a Project Gutenberg book.")
    parser.add_argument("--gutenberg-id", type=int, default=55, help="book number on gutenberg.org (default: 55, Oz)")
    parser.add_argument("--novel-id", default="oz", help="short name used for the data files (default: oz)")
    args = parser.parse_args()

    raw = raw_text_path(args.novel_id)
    if not raw.exists():
        print(f"Downloading Gutenberg book {args.gutenberg_id} ...")
        raw.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(GUTENBERG_URL.format(id=args.gutenberg_id)) as response:
            raw.write_bytes(response.read())

    chapters = split_chapters(strip_gutenberg(raw.read_text(encoding="utf-8")))
    if not chapters:
        raise SystemExit("No chapter headings found (expected lines like 'Chapter I' or 'CHAPTER 1').")
    save_chapters(chapters, chapters_path(args.novel_id))
    for chapter in chapters:
        print(f"{chapter.number:>3}  {chapter.word_count:>5} words  {chapter.title}")
    print(f"Saved {len(chapters)} chapters to {chapters_path(args.novel_id)}")


if __name__ == "__main__":
    main()
