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
- Gate 1 passed: 475 blocks, verifier 0 errors, coverage 0 uncovered (66 terms resolved in `coverage_decisions.tsv`). Fixed curly-apostrophe handling in the verifier (entity warnings 638 -> 540) and added FAR tagging. Filled 5 missing `NEW:` lines. Removed `Chapter_Notes/parts/` after merge.
- Phase 2 started: `tools/extract_facts.py` (facts.jsonl 13,077 facts, entities.tsv 2,493 canonical entities of which 706 need a file under the Gate 2 rule), `tools/fold_suggest.py`, `ledgers/alias_overrides.tsv` (41 reviewed first-name folds). Added item 2.3 (stricter coverage check) to the plan.
- Phase 2 (cont.): resolved the 54 alias conflicts (`tools/resolve_conflicts.py`); strict `check_coverage.py` with plural/honorific variants; `auto_gap_decisions.py`, `make_gap_work.py`, `merge_gap_decisions.py`; 3 agents classified 271 uncovered census terms (alias 90, stop 36, entity 145); heuristic fact kinds in `extract_facts.py`; manual fact-less entities in `entities.tsv`. Coverage: 0 of 2,010 uncovered under the strict rule.
- Phase 2.2 (full entity review): `make_entity_work.py` built work packages; 18 agents decided fold/split/topic/keep/homonym for all 2,601 entities and re-verified the 271 coverage decisions; `merge_entity_decisions.py` applies them idempotently against a frozen pre-review snapshot (`ledgers/work/entities_base.tsv`); 8 verifiers independently checked all 351 folds and splits (15 rejected, 1 uncertain, all left unmerged). Added `ambiguous` decision kind, `protected` never-merge handling, alias-cycle breaker, stable fact ids (`sid`), per-fact and composite-split overrides. Fixed mis-merges found on the way (Golem/Gorgon species, Seborn, inn door, Odveig = Sacra). Entities 2,482 -> 2,168; coverage 0 of 2,010 uncovered.
- Phase 2.2 closed: 12 verifiers checked all 766 older alias pairs (633 ok, 130 reject, 3 uncertain); rejected ones are never-merge. Side findings fixed: ksmvr, issa. Added decisions for Professor, Revalantor, Lord Kallinad, Kallinad, Issa, Brothers, Brother. Stable pipeline: merge_entity_decisions -> merge_gap_decisions -> extract_facts (run twice, identical outputs). Coverage 0 of 2,010 uncovered; verify_notes 0 errors; 13,136 facts, 0 orphans, 2,181 entities (731 with >=15 facts or 2+ chapters).

## 2026-11-06
- Phase 2.4: `make_kind_work.py` / `merge_kind_decisions.py`; 22 agent chunks reviewed all 13,136 fact kinds (heuristic wrong on 5,959) and added 340 supersession links on 293 facts (0 invalid). `extract_facts.py` now applies `fact_kinds.tsv` (`kind_source: reviewed`, `supersedes`, `superseded_by`). Final kinds: event 5,783, fact 5,160, belief 1,013, state 852, rel 171, reveal 157. Pipeline stable (two runs identical), coverage 0 of 2,010 uncovered, verify_notes 0 errors. Phase 2 complete; Gate 2 met (every entity with >=15 facts or 2+ chapters is a ledger row, 0 orphan facts).

