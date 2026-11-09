# Build Plan (phased, with gates)

Status legend: [x] done, [~] in progress, [ ] not started.

## Phase 0: foundation (done before any content)
- [x] 0.1 git repository, .gitignore (Source_Text not committed)
- [x] 0.2 split 19 books into 510 chapter/meta files; index JSON + README (split.py)
- [x] 0.3 integrity checks (check_split.py): ids unique, TOC order matches, every volume numbering complete, 99.97% words placed
- [x] 0.4 reader/grep tool with citation output (rd.py)
- [x] 0.5 deterministic catalogs: bracket terms (classes/skills/spells/conditions, level events) and capitalised-name census (scan_brackets.py, scan_names.py)
- [x] 0.6 project structure and process document
- [x] 0.7 notes verifier (verify_notes.py; report in src/ledgers/verify_report.txt): parses Chapter_Notes, checks every `(Lnn)` exists and named entities occur within +-6 lines
- [x] 0.8 aliases merged (ledgers/aliases.tsv, alias_conflicts.tsv, open_questions.md via tools/merge_ledgers.py); stoplist seeded

## Phase 1 (DONE 2026-10-31, gate passed): study pass, front to back, once (Chapter_Notes/bNN.md)
One block per chapter in the format of `src/Chapter_Notes/README.md`. Order = reading order (seq 1..510). Also appended while reading: `ledgers/aliases.tsv`, `ledgers/open_questions.md`, `ledgers/entities_seen.tsv`.
Gate 1: every chapter has a block; verify_notes.py reports zero dangling cites; all census terms >=15 occurrences are covered (entity, alias or stoplist).

## Phase 2 (DONE 2026-11-06, Gate 2 passed): entity ledger
Merge notes into `ledgers/facts.jsonl` (entity, kind, text, cite, seq). Resolve aliases, split homonyms. Phase 2 items:
- [x] 2.1 `extract_facts.py`: parse notes into `ledgers/facts.jsonl` (13,077 facts), group by canonical entity via the alias map, split joint-subject "A and B" facts across both entities (307); writes `entities.tsv` and `entity_report.txt`
- [x] 2.2 (DONE: all 2,601 entities reviewed; folds/splits and all 766 older alias pairs independently verified; 130+15 rejected merges left unmerged) resolve `alias_conflicts.tsv`, split homonyms, fold surname/title variants (Ryoka vs Ryoka Griffin)
- [x] 2.3 (strict rule live: 0 of 2,010 census terms >=15 uncovered; 271 gaps decided in `coverage_decisions_gap.tsv`, 145 as fact-less manual entities) strengthen `check_coverage.py`: a census term counts as covered only if it resolves to a canonical entity in the entity ledger (or is stoplisted / a bracket term), not merely because it appears in some note line; turn the `entity` rows in `coverage_decisions.tsv` into real ledger entities
- [x] 2.4 (DONE: all 13,136 facts reviewed by agents; 5,959 kind changes; 293 facts carry 340 supersession links, 0 invalid; `fact_kinds.tsv`, `merge_kind_decisions.py`) classify fact kinds (`fact`/`rel`/`event`/`belief`/`reveal`/`state`) and set `seq` per fact; supersession links for retcons
- [x] 2.5 entity-ledger report and orphan-fact check (0 orphan facts; `entity_report.txt`; every entity with >=15 facts or 2+ chapters is a row in `entities.tsv`)
Gate 2: each entity with >=15 facts or 2+ chapters has a file; no orphan facts.

## Phase 3: entity files and topic files
Primer, cosmology/system (levels, classes, skills, Names, gods, dungeons), species, nations/cities, organisations, characters, items, events/wars, timeline per volume. Written once to the entity rules in the structure doc; each claim cited.
- [x] 3.1 entry format (`ENTRY_FORMAT.md`) and `lint_entities.py` (cites checked against the text, claim seq derived)
- [x] 3.2 foundations drafted and independently verified: 01 primer, 02 levels/classes/skills, 03 magic, 04 cosmology/gods/Names/dungeons, 05 core species, 06 other species, 07 creatures (1,903 claims; second-pass gaps in DEF-029..DEF-035)
- [x] 3.3 places and organisations (74 + 104 files, `Entities/Places`, `Entities/Organisations`)
- [ ] 3.4 characters (entity files from `facts.jsonl` plus the text; large entities need supersession links across pieces, DEF-028)
- [x] 3.5 items, events, titles, concepts, classes and untyped entities (DEF-014, DEF-018 for entities with a 'needs file' flag; timeline per volume still to do)
- [ ] 3.6 foundations pass 2 (DEF-029..DEF-035) and open-question resolution (DEF-036)

## Phase 4: verification
verify2-style automated pass (quotes/numbers within +-2 lines of cite), independent re-read of sampled chapters, lint (headers, links, cite validity, one-home-per-fact).

## Phase 5: lorebook export
`build_lorebook.py` cuts facts at chosen seq cutoffs (every book boundary and the full text) and writes SillyTavern world-info JSON + Markdown. Gate 5: entries contain only facts with seq <= cutoff (checked by script), keys include aliases, entries within the token budget.
