# TWI Compendium: Changelog

## 2026-10-31
- Regenerated the 510 chapter files in `src/Source_Text/` with `split.py` (they were missing).
- Study pass: notes for all 461 chapters across Books 1-19 (`Chapter_Notes/b01..b19.md`), plus Author's Notes seq 151 and 177. Run by parallel agents in 5-chapter chunks.
- Added `tools/merge_notes.py`, `tools/verify_notes.py` (0 hard errors, 634 advisory warnings) and `tools/merge_ledgers.py`.
- Merged ledgers: `aliases.tsv` (887 pairs), `alias_conflicts.tsv` (54), `open_questions.md` (622).
- Created the git repository and pushed to `WAGEDATWAR/twi-compendium`.
- Notes blocks for the 12 remaining Author's Notes (Books 5-16); 475 blocks total, verifier still 0 errors.
- Added `tools/check_coverage.py` (Gate 1 name coverage) and a seed `ledgers/stoplist.txt`; 2010 census terms >=15 occurrences, 66 uncovered.
- Added scaffolding: `DEFERRALS.md`, `SUGGESTIONS.md`, `DECISIONS.md`, `CHANGELOG.md`, `AGENTS.md`.
