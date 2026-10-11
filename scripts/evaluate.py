"""Step 5: evaluate the continuity checker on the book with injected contradictions.

1. Build the test corpus: the prepared book with data/test_corpus/<novel>_injections.json applied.
2. Extract both versions (chapters whose text is unchanged reuse the saved extraction).
3. Run the full pipeline (store, retrieve, check) on the original book and on the test corpus.
4. Score the flags against the injections and write the results to data/results/.

    python scripts/evaluate.py                    # everything (slow: several hours on an 8 GB laptop)
    python scripts/evaluate.py --reuse-flags      # only re-score saved flags
    python scripts/evaluate.py --chapters 8       # a quick trial on the first 8 chapters
"""

import argparse
import json
import time
from datetime import date

from continuity_editor.checking.prompts import CHECK_VERSION
from continuity_editor.evaluation import apply_injections, evaluate, load_injections, render_report
from continuity_editor.extraction import extract_novel, load_chapters, save_chapters
from continuity_editor.extraction.prompts import EXTRACTION_VERSION
from continuity_editor.graph import Neo4jConnection, apply_schema
from continuity_editor.llm import LLMClient
from continuity_editor.paths import DATA_DIR, chapters_path, extraction_cache_dir, results_dir
from continuity_editor.pipeline import load_flags, run_novel, save_flags


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the checker on injected contradictions.")
    parser.add_argument("--novel-id", default="oz")
    parser.add_argument("--title", default="The Wonderful Wizard of Oz")
    parser.add_argument("--chapters", type=int, help="only the first N chapters (for a quick trial)")
    parser.add_argument("--reuse-flags", action="store_true", help="re-score flags saved by an earlier run")
    parser.add_argument("--skip-clean", action="store_true", help="don't run the checker on the original book")
    args = parser.parse_args()

    clean = load_chapters(chapters_path(args.novel_id))
    injections = load_injections(DATA_DIR / "test_corpus" / f"{args.novel_id}_injections.json")
    injected = apply_injections(clean, injections)
    if args.chapters:
        clean, injected = clean[: args.chapters], injected[: args.chapters]
        injections = [i for i in injections if i.chapter <= args.chapters]
    test_id = f"{args.novel_id}_injected"
    save_chapters(injected, chapters_path(test_id))

    out = results_dir()
    out.mkdir(parents=True, exist_ok=True)
    clean_path, injected_path = out / f"flags_{args.novel_id}.json", out / f"flags_{test_id}.json"
    llm = LLMClient(cache_dir=DATA_DIR / "processed" / "llm_cache")  # a re-run reuses the judge's answers
    meta = {"date": date.today().isoformat(), "model": llm.model, "extraction": f"v{EXTRACTION_VERSION}",
            "checker": f"v{CHECK_VERSION}", "chapters": str(len(clean))}

    if args.reuse_flags:
        clean_flags = load_flags(clean_path) if clean_path.exists() else None
        injected_flags = load_flags(injected_path)
    else:
        llm.verify()
        with Neo4jConnection() as conn:
            conn.verify()
            apply_schema(conn)
            print("Extracting (saved chapters are reused) ...")
            clean_extractions = extract_novel(llm, args.novel_id, clean, extraction_cache_dir())
            injected_extractions = extract_novel(llm, test_id, injected, extraction_cache_dir())

            # The test corpus first: it gives the main results, so they are saved even if the
            # (optional, slow) run on the original book is interrupted.
            start, calls = time.perf_counter(), llm.usage["calls"]
            injected_flags = run_novel(conn, llm, test_id, f"{args.title} (test corpus)", injected, injected_extractions)
            save_flags(injected_flags, injected_path)
            meta["test corpus check"] = f"{llm.usage['calls'] - calls} LLM calls, {time.perf_counter() - start:.0f}s"

            clean_flags = None
            if not args.skip_clean:
                start, calls = time.perf_counter(), llm.usage["calls"]
                clean_flags = run_novel(conn, llm, args.novel_id, args.title, clean, clean_extractions)
                save_flags(clean_flags, clean_path)
                meta["original book check"] = f"{llm.usage['calls'] - calls} LLM calls, {time.perf_counter() - start:.0f}s"

    result = evaluate(injected_flags, injections)
    (out / "evaluation.json").write_text(json.dumps({"meta": meta, **result.model_dump()}, indent=1), encoding="utf-8")
    report = render_report(result, injected_flags, clean_flags, injections, meta)
    (out / "evaluation_report.md").write_text(report, encoding="utf-8")

    print(f"Recall: {result.detected}/{result.contradictions} injected contradictions detected ({result.recall:.0%})")
    if result.precision is not None:
        print(f"Precision: {result.true_positive_flags}/{result.flags} flags point at an injection ({result.precision:.0%})")
    if clean_flags is not None:
        print(f"False alarms on the original book: {len(clean_flags)}")
    print(f"Report: {out / 'evaluation_report.md'}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(f"Error: {exc}")
