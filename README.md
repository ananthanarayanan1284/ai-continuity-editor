# AI Continuity Editor for Long-Form Fiction

Reads a novel chapter by chapter, builds a "story bible" of characters, places, events and world facts in a Neo4j graph, and flags contradictions as each new chapter is added. Each flag cites both conflicting sentences, explains the conflict, and carries a confidence tier: **high** (a direct clash), **medium** (probably a mistake) or **low** (a surface mismatch that context may explain).

Everything is free to run. The LLM is an open-source model running on your own computer through [Ollama](https://ollama.com): no account, no API key, and the manuscript never leaves the machine. The graph lives in a free Neo4j AuraDB instance.

Capstone project: M.Sc. Data Science & Geoinformatics, Digital University Kerala.

## How it works

```
chapter text
  │  Step 2  extraction (local LLM, two passes per ~900-word chunk)
  │          1. entities: characters, places, world elements
  │          2. facts and events about those entities, each with a quote
  │             that is checked against the text
  ▼
story bible in Neo4j (append-only: facts are never overwritten)
  │  Step 3  entity resolution ("the Woodman" = "the Tin Woodman")
  │          targeted retrieval: earlier facts about every entity the chapter mentions
  ▼
Step 4  checker: for each new fact, the related earlier facts are picked with text
        rules, and the LLM judges only real candidates → flag + reason + tier
  ▼
Step 5  evaluation: 20 contradictions injected into the book → precision and recall
```

## Setup (one time)

1. **Python 3.11 or newer.** macOS ships Python 3.9, which is too old. Check with `python3 --version`.
2. **Ollama (the free local LLM):**
   - Install it from https://ollama.com/download and open it once. After that it runs in the menu bar.
   - Download the model in Terminal: `ollama pull qwen3:4b-instruct` (2.5 GB; runs on a Mac with 8 GB of memory).
3. **Neo4j AuraDB Free** (a cloud database: nothing to install, no Docker):
   - Go to https://console.neo4j.io, sign in, and create a **Free** instance.
   - Download the credentials `.txt` file when it's offered. The password is shown only once.
4. **Secrets file:** `cp .env.example .env`, then fill in the Neo4j values from the credentials file. The LLM needs no key.
5. **Virtual environment and packages:**
   ```bash
   python3 -m venv .venv            # use your Python 3.11+ here
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .                  # makes `import continuity_editor` work everywhere
   python -m ipykernel install --user --name continuity-editor --display-name "Continuity Editor (.venv)"
   ```
   The last command registers the `.venv` as a Jupyter kernel, which the notebooks are set to use.
6. **Check both services:**
   ```bash
   python scripts/check_llm.py      # Ollama running, model downloaded, answers in JSON
   python scripts/init_db.py        # Neo4j reachable, constraints and indexes created
   ```
7. **VS Code:** open a notebook. The kernel (top right) should read **Continuity Editor (.venv)**. If it doesn't, click it and choose **Select Another Kernel… → Jupyter Kernel… → Continuity Editor (.venv)**. See *Troubleshooting* if the kernel isn't listed.

AuraDB Free pauses after a few days without use. If the connection fails, resume the instance in the Aura console.

## Running it

```bash
python scripts/prepare_novel.py     # download The Wonderful Wizard of Oz and split it into 24 chapters
python scripts/extract_novel.py     # Step 2: extract every chapter (about 2 hours on an 8 GB MacBook Air)
python scripts/evaluate.py          # Steps 3-5: build the story bible, check it, score the injected contradictions
```

Every step saves its work, so each command can be stopped and started again. Extractions are saved per chapter under a fingerprint of the chapter text: the evaluation's edited copy of the book re-extracts only the chapters that were changed, and a chapter is redone only if its text, the model or the extraction code changes. `python scripts/evaluate.py --reuse-flags` re-scores saved results without running the model.

These jobs keep the laptop busy for hours. On a Mac, prefix a command with `caffeinate -i` so the Mac doesn't sleep, and keep it plugged in with the lid open.

## Running on a free Kaggle GPU

A laptop with 8 GB can only run a small model, slowly. `kaggle/run_on_kaggle.ipynb` runs the whole evaluation on Kaggle's free GPUs instead, for the small model and a bigger one (`qwen3:14b`), and saves the results of each.

1. Create a free Kaggle account and verify your phone number (needed for GPUs and internet access).
2. Zip the project **without `.env` and `.venv`**, and upload it as a Kaggle dataset (**Create → New Dataset**).
3. Import the notebook (**Create → New Notebook → File → Import Notebook**), then follow the checklist at its top: GPU T4 x2, internet on, the three `NEO4J_…` secrets, the dataset as input.
4. **Save Version → Save & Run All (Commit)**, and download `results` from the version's **Output** tab when it finishes.

## Notebooks

| Notebook | Shows |
|---|---|
| `01_neo4j_connection_and_schema` | the graph schema and the append-only fact history on a toy example |
| `02_extraction` | the entities, facts and events extracted from one chapter |
| `03_retrieval_and_checking` | a two-chapter story checked end to end: the flag, what was retrieved, the link in the graph |
| `04_evaluation` | precision and recall on the injected contradictions |

## Evaluation (Step 5)

`data/test_corpus/oz_injections.json` lists 20 contradictions injected into later chapters of *The Wonderful Wizard of Oz*, each contradicting a detail established earlier:

| Category | Injected | Examples |
|---|---|---|
| characterisation | 7 | Toto becomes "the little white dog" (chapter 1: "a little black dog"); the Lion asks Oz for a heart instead of courage |
| factual detail | 3 | Uncle Henry is "the village blacksmith" (chapter 1: a farmer); Dorothy's shoes become golden |
| world building | 6 | the Golden Cap works without limit (chapter 12: three times); Emerald City residents never wear spectacles |
| timeline | 4 | the Scarecrow stood in the cornfield "for many long years" (chapter 4: made the day before yesterday) |

Each has an expected tier. Two are deliberately ambiguous and expected to be **low**, like the project brief's lighting example: Toto's black coat "looked quite green through the glasses". Two more edits are harmless restatements ("controls") that must not be flagged.

A flag counts as a hit when it cites the injected sentence. **Recall** is the share of injected contradictions hit; **precision** is the share of flags that hit one. The full results, including every false alarm with the checker's reason, are in `data/results/evaluation_report.md`.

<!-- RESULTS -->

## Project layout

```
continuity_editor/
  config.py          settings from .env (Neo4j and LLM separately)
  llm.py             local LLM client (Ollama): validated JSON answers, token usage
  paths.py           where data files live
  extraction/        Step 2: chapters, chunks, two-pass extraction, quote checking, caching
  graph/             Neo4j: connection, schema, node models, append-only writer
  retrieval/         Step 3: entity resolution and per-entity fact history
  checking/          Step 4: prior-fact selection and the tiered LLM judge
  pipeline.py        Steps 2-4 chapter by chapter, as a writer would add them
  evaluation/        Step 5: test corpus, scoring, report
data/
  raw/               source novels (not committed)
  processed/         chapters and saved extractions (not committed)
  test_corpus/       the injected contradictions (committed: the ground truth)
  results/           flags, scores and the evaluation report
notebooks/           01-04, one per step
scripts/             check_llm, init_db, prepare_novel, extract_novel, evaluate
tests/               pytest; tests needing Ollama or Neo4j skip when they aren't available
```

## Graph schema

Facts are **nodes**, never overwritten properties, so every version of a detail is kept with the chapter that stated it:

```
(:Novel)-[:HAS_CHAPTER]->(:Chapter)-[:NEXT]->(:Chapter)
(:Chapter)-[:MENTIONS]->(:Entity)          Entity = Character | Location | WorldElement
(:Entity)-[:HAS_FACT]->(:Fact)-[:STATED_IN]->(:Chapter)
(:Character)-[:PARTICIPATES_IN]->(:Event)-[:OCCURS_AT]->(:Location)
(:Event)-[:DESCRIBED_IN]->(:Chapter),  (:Event)-[:PRECEDES]->(:Event)
(:Fact)-[:CONTRADICTS {confidence, reason}]->(:Fact)     a flag, stored in the story bible
```

`Fact.category` follows the ConStory-Bench taxonomy: characterisation, factual_detail, timeline, world_building, narrative_style.

## Choosing a model

The default, `qwen3:4b-instruct`, is chosen to fit an 8 GB laptop. On a computer with 16 GB or more you can try a larger model such as `gemma3:12b`: run `ollama pull gemma3:12b` and set `LLM_MODEL=gemma3:12b` in `.env`. Results depend on the model, so use the same model for every run you compare.

## Limitations

- **A small model.** A 4-billion-parameter model sometimes labels the same thing differently in different chapters, misses facts, or records passing actions as facts. The pipeline checks every quote against the text and filters obvious noise, but extraction quality bounds what the checker can find.
- **Facts, not events.** The checker compares stated facts. A contradiction that exists only in what *happens* (event order, who was where) is out of its reach unless the text also states it as a fact.
- **Name matching is rule-based.** Synonyms such as "the City of Emeralds" and "the Emerald City" stay separate entities.
- **A small test set.** Twenty hand-made injections in one book give indicative, not definitive, precision and recall.

## Tests

```bash
pytest                    # offline tests always run; live tests run once Ollama and .env are set up
```

## Troubleshooting

- **VS Code shows only "Python 3.9" or a "cpython-3.12…" kernel and asks to install ipykernel.** Don't install it: that is the wrong Python. If **Continuity Editor (.venv)** isn't under **Jupyter Kernel…** either, start a Jupyter server from the project folder with `.venv/bin/jupyter server --no-browser`, copy the `http://localhost:8888/?token=…` address it prints, and in VS Code choose **Select Another Kernel… → Existing Jupyter Server…**, paste it, then pick **Continuity Editor (.venv)**. Keep that terminal open while you work.
- **"Could not reach Ollama".** Open the Ollama app (it lives in the menu bar).
- **"Could not reach Neo4j".** Resume the AuraDB instance at https://console.neo4j.io.
