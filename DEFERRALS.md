# TWI Compendium: Deferral Ledger

Single home for everything deliberately put off or left unfinished. Anything written as "later", "deferred", "for now" or "not yet" in a doc, commit or note gets a row here in the same change.

**Status:** `open` (owed) · `scheduled` (a phase/gate owns it) · `doing` · `done` · `dropped` (say why).
**Rules:** every row has an owner (a plan item or gate in `TODO_Build_Plan.md`); a gate is not passed while an `open`/`scheduled` row owned by it exists; when a row lands, mark it `done` with the commit; when dropped, say why.

| # | Item | Owed since | Owner | Status |
|---|---|---|---|---|
| DEF-001 | Chapter_Notes blocks for the 12 remaining Author's Notes (Meta seq 215-461) | 2026-10-31 | Gate 1 | done (this commit; Meta pages other than Author's Notes intentionally not noted) |
| DEF-002 | Stoplist ledger (non-entity capitalised words) for the names census | 0.8 | Gate 1 | open |
| DEF-003 | Gate 1 coverage check: every census term with >=15 occurrences is an entity, alias or stoplisted (needs a `check_coverage.py`) | Phase 1 | Gate 1 | open |
| DEF-004 | Triage the entity warnings in `ledgers/verify_report.txt` (634 lines, 4.8%): fix cite or entity name where it is a real mismatch | 2026-10-31 | Gate 1 | open |
| DEF-005 | Resolve `ledgers/alias_conflicts.tsv` (54 aliases mapped to more than one canonical); decide homonym vs same entity | 2026-10-31 | Phase 2 | open |
| DEF-006 | Resolve `ledgers/open_questions.md` (622 items) before export; each answered against the text or kept as a documented ambiguity | Phase 1 | Gate 5 | open |
| DEF-007 | Re-verify cites agents flagged as unchecked or inferred: 7.55E (b19), 4.30 and 4.31 (b05), 6.12K-6.16 (b10), Interlude_B09_1 (b09), 4.49 and "Peace" lines (b06) | 2026-10-31 | Phase 4 | open |
| DEF-008 | Six Book 1 blocks lack a `NEW:` line (warnings in `verify_report.txt`); add them | 2026-10-31 | Gate 1 | open |
| DEF-009 | Three cross-chapter cites (e.g. "6.31 L860") are not machine-checked; either rewrite as same-chapter cites or extend the verifier | 2026-10-31 | Phase 4 | open |
| DEF-010 | Many blocks run 5-8 KB against the 1.5-3 KB format target; leave until Phase 2 shows whether it hurts fact extraction | 2026-10-31 | Phase 2 | scheduled |
| DEF-011 | `Chapter_Notes/parts/` is redundant after `merge_notes.py`; remove from the repo once Gate 1 passes | 2026-10-31 | Gate 1 | open |
| DEF-012 | Phases 2-5 (entity ledger, entity files, verification, lorebook export) | project start | Phases 2-5 | scheduled |
| DEF-013 | Appendices (Glossary, Name_Index, Source_Register) listed in the structure doc; Change_Log is covered by root `CHANGELOG.md` | project start | Phase 3 | scheduled |
