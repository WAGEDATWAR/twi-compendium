# AGENTS.md: working notes for automated agents

Project: **The Wandering Inn Compendium**, a cited, spoiler-cuttable reference for a lorebook (Books 1-19, web-serial vols 1-7).

## Read first
1. `00_Project_Structure.md`: purpose, cite format, entity and fact rules.
2. `TODO_Build_Plan.md`: phases and gates.
3. `DEFERRALS.md`: what is owed; `DECISIONS.md`: what is locked; `SUGGESTIONS.md`: ideas awaiting triage.
4. `src/Chapter_Notes/README.md`: the block format.

## Golden rules
- The book text wins. Every `+ ~ ! =` note line ends with a cite `(Lnn)` you actually read. Never write from memory.
- Never commit book text (see D-001). Never push unless asked.
- Anything you put off goes in `DEFERRALS.md`; ideas go in `SUGGESTIONS.md`; choices in `DECISIONS.md`; log each session in `CHANGELOG.md`.
- Scripts are files, not one-off heredocs. Run Python with `python -I`.

## Commands (from the project root)
- `python -I src/tools/split.py <dir with b1.txt..b19.txt>`: rebuild chapter files from the raw e-books in `src/The Wandering Inn/` (copy them to `bN.txt` names first).
- `python -I src/tools/rd.py`: reader/grep with citation output.
- `python -I src/tools/merge_notes.py`: merge `Chapter_Notes/parts/*` into `bNN.md`.
- `python -I src/tools/verify_notes.py`: writes `src/ledgers/verify_report.txt`; exit 1 on hard errors.
- `python -I src/tools/merge_ledgers.py`: rebuild merged alias and open-question ledgers.
- `python -I src/tools/lint_entities.py [--emit] [file ...]`: lint Phase 3 entry files (see `ENTRY_FORMAT.md`); `--emit` writes `ledgers/entry_claims.jsonl`.
- `python -I src/tools/show_claims.py <file> [lo [hi]]`: claims beside their cited text (for verification). `apply_verification.py [--dry] [tag ...]` applies decisions from `tools/cache/verify/*.tsv`.
- `python -I src/tools/make_foundation_work.py`: seed packets for foundation files (cache, gitignored).
- Source text: clone `WAGEDATWAR/twi-source` and copy `Book_*` into `src/Source_Text/` (gitignored, D-001).

## Pitfalls seen
- Note files may start with a UTF-8 BOM; read with `utf-8-sig`.
- PowerShell 5 shows UTF-8 as mojibake; the files are fine, check with Python.
- Agents hit usage limits mid-run: keep chunks small, write after every chapter, and make reruns resume from existing part files.
- `bNN.md` numbering is the e-book number; chapter ids carry the serial (e.g. Book 3 contains `1.00D`).
