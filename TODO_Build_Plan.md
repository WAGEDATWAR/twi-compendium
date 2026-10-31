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

## Phase 2: entity ledger
Merge notes into `ledgers/facts.jsonl` (entity, kind, text, cite, seq). Resolve aliases, split homonyms. Gate 2: each entity with >=15 facts or 2+ chapters has a file; no orphan facts.

## Phase 3: entity files and topic files
Primer, cosmology/system (levels, classes, skills, Names, gods, dungeons), species, nations/cities, organisations, characters, items, events/wars, timeline per volume. Written once to the entity rules in the structure doc; each claim cited.

## Phase 4: verification
verify2-style automated pass (quotes/numbers within +-2 lines of cite), independent re-read of sampled chapters, lint (headers, links, cite validity, one-home-per-fact).

## Phase 5: lorebook export
`build_lorebook.py` cuts facts at chosen seq cutoffs (every book boundary and the full text) and writes SillyTavern world-info JSON + Markdown. Gate 5: entries contain only facts with seq <= cutoff (checked by script), keys include aliases, entries within the token budget.
