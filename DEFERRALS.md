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
| DEF-005 | Resolve `ledgers/alias_conflicts.tsv` (54 aliases mapped to more than one canonical) | 2026-10-31 | Phase 2 | done (32 unions, 41 never-merge titles in `alias_overrides.tsv`; `resolve_conflicts.py`) |
| DEF-006 | Resolve `ledgers/open_questions.md` (622 items) before export; each answered against the text or kept as a documented ambiguity | Phase 1 | Gate 5 | open |
| DEF-007 | Re-verify cites agents flagged as unchecked or inferred: 7.55E (b19), 4.30 and 4.31 (b05), 6.12K-6.16 (b10), Interlude_B09_1 (b09), 4.49 and "Peace" lines (b06) | 2026-10-31 | Phase 4 | open |
| DEF-008 | Six Book 1 blocks lacked a `NEW:` line; five were found and filled from their own entity lists (1.00, 1.03, 1.08, 1.11, Interlude_B01_1). Auto-derived, not re-read | 2026-10-31 | Gate 1 | done |
| DEF-009 | Three cross-chapter cites (e.g. "6.31 L860") are not machine-checked; either rewrite as same-chapter cites or extend the verifier | 2026-10-31 | Phase 4 | open |
| DEF-010 | Many blocks run 5-8 KB against the 1.5-3 KB format target; leave until Phase 2 shows whether it hurts fact extraction | 2026-10-31 | Phase 2 | scheduled |
| DEF-011 | `Chapter_Notes/parts/` removed after merge (backup of pre-merge notes was in the OS temp folder only); `merge_notes.py` is now a no-op unless new part files appear | 2026-10-31 | Gate 1 | done |
| DEF-012 | Phases 2-5 (entity ledger, entity files, verification, lorebook export) | project start | Phases 2-5 | scheduled |
| DEF-013 | Appendices (Glossary, Name_Index, Source_Register) listed in the structure doc; Change_Log is covered by root `CHANGELOG.md` | project start | Phase 3 | scheduled |
| DEF-014 | Create entity files/entries for every `entity` row in `ledgers/coverage_decisions.tsv` (about 25 species, ranks, factions, unresolved epithets such as The Centauress and Lizardman) | 2026-10-31 | Phase 3 | scheduled |
| DEF-015 | Strengthen `check_coverage.py` so a term must resolve to a canonical ledger entity | 2026-10-31 | Phase 2 (2.3) | done (strict rule live; 0 uncovered) |
| DEF-016 | Remaining fold suggestions | 2026-10-31 | Phase 2 (2.2) | done (superseded by the full entity review: every entity has a decision in `entity_meta.tsv` / `alias_overrides.tsv`) |
| DEF-017 | 1-2 fact entities | 2026-10-31 | Phase 2 (2.2) | done (reviewed: 1,345 single-fact entities remain as kept minor entities or topics) |
| DEF-018 | About 126 manual entities (`needs_file=M` in `entities.tsv`, from `coverage_decisions_gap.tsv`) have no facts yet; Phase 3 must fill each from the text and cite it | 2026-10-31 | Phase 3 | scheduled |
| DEF-019 | Agent-made coverage decisions rested on 1-3 lookups each. Review the guesses: Minos -> house of minos, King of Duels -> raelt leysars, Minotauress -> minotaurs, Romeo/Juliet -> the play entity, Gorgon = Commander Uxel; and the unresolved entities Cade, Ser Slayer, Bezha, Bishop, Carven City, Thunderfur, Facestealer, Sharphorns | 2026-10-31 | Phase 4 | scheduled |
| DEF-020 | Fact kinds are wording heuristics (fact 10.6k, event 977, belief 877, state 442, reveal 70, rel 63); sample-check them, and build supersession links (`supersedes=`) for retcons | 2026-10-31 | Phase 2 (2.4) / Phase 4 | open |
| DEF-021 | 453 `topic` entities (levelling, magic, villagers, soldiers...) and 1,345 single-fact minor entities need a home: their facts must land in topic files or grouped minor-entity files in Phase 3 (Gate 2 "no orphan facts"). `entity_meta.tsv` has the decision and optional `home` | 2026-10-31 | Phase 3 | scheduled |
| DEF-022 | Reviewed `keep` decisions were made without comparing kept pairs against each other; Phase 3 may still find duplicates (one thing under two kept keys). Use `fold_suggest.py` / candidate lists during entity-file writing | 2026-10-31 | Phase 3 | scheduled |
| DEF-023 | Verifier follow-ups logged but not all applied: `drowned folk` (also holds a generic Drowned Man species fact), `goblin`/`goblins` and `trolls`/`troll` singulars that also hold individual facts, `antinium hives` -> `antinium hive` (Silent Hive), `celum gate` (uncertain, not merged) | 2026-10-31 | Phase 3 | scheduled |
| DEF-024 | 94 entities in `entities.tsv` have no `review`/`etype` (41 are canonical fold targets whose own fold was cycle-skipped, 29 were created by un-doing bad merges, 125 are fact-less manual entities with an etype from the gap decisions); assign etype when writing entity files | 2026-10-31 | Phase 3 | scheduled |
| DEF-025 | 133 older alias pairs were rejected by the independent verifier and are now never-merge rows (`2.2 review: alias rejected by verifier` in `alias_overrides.tsv`); each leaves a separate entity or an unresolved name that Phase 3 must place (some may need an `ambiguous` or `entity` decision) | 2026-10-31 | Phase 3 | scheduled |
| DEF-026 | The 78 alias rows and 157 entity rows of `coverage_decisions_gap.tsv` were reviewed once by a second agent, not independently verified like the folds; sample-check in Phase 4 | 2026-10-31 | Phase 4 | scheduled |

