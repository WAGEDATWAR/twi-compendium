# TWI Compendium: Deferral Ledger

Single home for everything deliberately put off or left unfinished. Anything written as "later", "deferred", "for now" or "not yet" in a doc, commit or note gets a row here in the same change.

**Status:** `open` (owed) · `scheduled` (a phase/gate owns it) · `doing` · `done` · `dropped` (say why).
**Rules:** every row has an owner (a plan item or gate in `TODO_Build_Plan.md`); a gate is not passed while an `open`/`scheduled` row owned by it exists; when a row lands, mark it `done` with the commit; when dropped, say why.

| # | Item | Owed since | Owner | Status |
|---|---|---|---|---|
| DEF-001 | Chapter_Notes blocks for the 12 remaining Author's Notes (Meta seq 215-461) | 2026-10-31 | Gate 1 | done (this commit; Meta pages other than Author's Notes intentionally not noted) |
| DEF-002 | Stoplist ledger (non-entity capitalised words) for the names census | 0.8 | Gate 1 | done (seed `ledgers/stoplist.txt`; `check_coverage.py` also ignores contractions and sentence-leading function words by rule) |
| DEF-003 | Gate 1 coverage: all 2010 census terms with >=15 occurrences covered (`check_coverage.py` exits 0). 66 were resolved through `ledgers/coverage_decisions.tsv` (alias / entity / bracket / stop) | Phase 1 | Gate 1 | done |
| DEF-004 | Review the verifier warnings in `ledgers/verify_report.txt` (540, 4.1% of fact lines; 198 tagged FAR = entity not within +-40 lines). Many are pronoun/epithet references (e.g. Teriarch unnamed in 1.09R), but FAR lines may hide wrong cites; sample-check them in Phase 4. Not a Gate 1 condition (gate = zero dangling cites) | 2026-10-31 | Phase 4 | scheduled |
| DEF-005 | Resolve `ledgers/alias_conflicts.tsv` (54 aliases mapped to more than one canonical); decide homonym vs same entity | 2026-10-31 | Phase 2 | open |
| DEF-006 | Resolve `ledgers/open_questions.md` (622 items) before export; each answered against the text or kept as a documented ambiguity | Phase 1 | Gate 5 | open |
| DEF-007 | Re-verify cites agents flagged as unchecked or inferred: 7.55E (b19), 4.30 and 4.31 (b05), 6.12K-6.16 (b10), Interlude_B09_1 (b09), 4.49 and "Peace" lines (b06) | 2026-10-31 | Phase 4 | open |
| DEF-008 | Six Book 1 blocks lacked a `NEW:` line; five were found and filled from their own entity lists (1.00, 1.03, 1.08, 1.11, Interlude_B01_1). Auto-derived, not re-read | 2026-10-31 | Gate 1 | done |
| DEF-009 | Three cross-chapter cites (e.g. "6.31 L860") are not machine-checked; either rewrite as same-chapter cites or extend the verifier | 2026-10-31 | Phase 4 | open |
| DEF-010 | Many blocks run 5-8 KB against the 1.5-3 KB format target; leave until Phase 2 shows whether it hurts fact extraction | 2026-10-31 | Phase 2 | scheduled |
| DEF-011 | `Chapter_Notes/parts/` removed after merge (backup of pre-merge notes was in the OS temp folder only); `merge_notes.py` is now a no-op unless new part files appear | 2026-10-31 | Gate 1 | done |
| DEF-012 | Phases 2-5 (entity ledger, entity files, verification, lorebook export) | project start | Phases 2-5 | scheduled |
| DEF-013 | Appendices (Glossary, Name_Index, Source_Register) listed in the structure doc; Change_Log is covered by root `CHANGELOG.md` | project start | Phase 3 | scheduled |
| DEF-014 | Create entity files/entries for every `entity` row in `ledgers/coverage_decisions.tsv` (about 25 species, ranks, factions, unresolved epithets such as The Centauress and Lizardman) | 2026-10-31 | Phase 3 | scheduled |
| DEF-015 | Strengthen `check_coverage.py` (a term must resolve to a canonical ledger entity, not just appear in a note line); re-run Gate 1 coverage under the stricter rule | 2026-10-31 | Phase 2 (item 2.3) | scheduled |
| DEF-016 | Remaining fold suggestions in `ledgers/fold_suggestions.tsv` (7 dominant, 20 ambiguous, e.g. Pawn, Olesm variants, Antinium, Witch/Califor): review and either add to `alias_overrides.tsv` or leave as separate entities | 2026-10-31 | Phase 2 (2.2) | open |
| DEF-017 | 1,682 single-fact entities in `entities.tsv`: many are fragments or misspellings of existing entities (e.g. "Gecko of Liscor" vs "Gecko"); sweep for folds or drop into topic files | 2026-10-31 | Phase 2 (2.2) | open |
