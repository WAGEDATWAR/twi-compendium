# TWI Compendium: Decision Log

Locked choices and provisional answers. `locked` (change only with a new entry) · `provisional` (cheap to reverse).

| # | Decision | Status |
|---|---|---|
| D-001 | Source text is never committed. `.gitignore` excludes `src/Source_Text/`, `src/raw_books/` and `src/The Wandering Inn/` (the raw e-books). Chapter files are regenerated with `tools/split.py` | locked |
| D-002 | Cites are physical line numbers in the chapter file: `(Book N, Ch<id> L<line>)`; notes use `(Lnn)` within a chapter block | locked |
| D-003 | The study pass is done in 5-chapter chunks by parallel agents (one agent cannot hold a whole book); each writes `Chapter_Notes/parts/bNN_pK.md`, then `tools/merge_notes.py` merges by seq into `bNN.md` (part file wins on duplicate) | locked |
| D-004 | Only Author's Notes get a notes block among the Meta pages; acknowledgements, copyright, about-the-author and further-reading pages do not | provisional |
| D-005 | Alias and open-question ledgers are written per chunk, then merged by `tools/merge_ledgers.py` into `aliases.tsv`, `alias_conflicts.tsv`, `open_questions.md`; per-chunk files are kept as sources | locked |
| D-006 | Change history lives in root `CHANGELOG.md` (replaces `Appendices/Change_Log.md` from the structure doc) | provisional |
| D-007 | Remote is `https://github.com/WAGEDATWAR/twi-compendium`, branch `main`; push only when the user asks | locked |
| D-008 | Verifier warnings (entity not near cite) are advisory; only format errors (no cite, cite beyond file, id/seq mismatch, missing `S:`) fail the run | provisional |
| D-009 | Phase 3 files follow `ENTRY_FORMAT.md`: every claim is one bullet ending in a cite group; claim `seq` is derived as the highest seq among its cites (no hand-written seq); checked by `tools/lint_entities.py`. Topic files live at the root as `NN_*.md`, entity files under `Entities/` | locked |
| D-010 | Foundation files (primer, levels/classes/skills, magic, cosmology, species, creatures) are written by parallel agents, one file per agent, each claim read in `Source_Text` with `rd.py` before it is written; the ledger facts are seeds, not sources | provisional |
| D-011 | Entity files live in `Entities/<TypeDir>/<Slug>.md` (Places, Organisations, Characters, Items, Events, Titles, Concepts, Classes, Spells, Other) and are written from ledger facts by agents that must read each cited passage (`show_claims.py` on a packet from `make_entity_batches.py`). Species and creature entities are homed in the foundation files 05/06/07 rather than duplicated as entity files; the consistency+depth pass must check every ledger fact has a home (entity file or foundation file) | locked |
| D-012 | Phase 3 order: 3.3 places+organisations, 3.5 small categories, 3.4 characters (largest, in waves), then a consistency+depth pass over all Phase 3 files (accuracy, cross-file consistency, coverage of ledger facts and of relevant text not yet captured) before Phase 4 | locked (user, 2026-11-08) |
