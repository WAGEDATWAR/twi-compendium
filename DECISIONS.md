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
