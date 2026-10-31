# The Wandering Inn Compendium: Project Structure and Build Process

*Open this first. It defines what is built, how facts are recorded, and why the process differs from the HWFWM compendium.*

## 1. Purpose

A reference for powering a **lorebook** (SillyTavern/Chub world-info JSON plus Markdown) that covers the whole of *The Wandering Inn* (pirateaba), Books 1-19 as supplied (web-serial volumes 1-7, chapters 1.00-7.55). Not a game system: the books' own levels/classes/skills are world facts and are recorded as such; no invented numbers.

Quality bar: **every fact in the lorebook is traceable to a cited line of the book text, and every lorebook can be cut exactly at any chapter** (no spoiler leaks by construction, not by keyword filter).

## 2. Lessons from the HWFWM build, and what is done differently here

| HWFWM experience (from its TODO_Build_Plan / TODO_Verification / tools README) | This project |
|---|---|
| Version control, linter and register builder were added late (Tier 0, after hundreds of scripted edits) | `git init` and tooling exist before any content; commit after every unit of work |
| Per-book free-prose "chapter notes" with weak cites ("notes", "wiki" tiers, "check?" items) | Per-chapter notes in a **parseable line format with line cites on every fact**; no wiki tier exists (source text only) |
| Register of claims built *after* the documents, then graded (3.5k ok / 243 near / 52 weak) | Facts are **born cited**; `verify_notes.py` checks each cited line exists and the claimed names/numbers occur near it |
| Spoilers by four coarse levels + keyword filter (`lorebook.py` "safety net, not a guarantee"; `held_back.txt`) | Each fact carries `seq` (first chapter where it is true *for the reader*); exporter cuts at any seq/book exactly. Reveals/retcons are separate dated facts |
| Missing names found by `name_scan.py` at the end (Thanh, Geneva, Maldonado...) | `scan_names.py` census runs **first**; coverage check is a gate before any export |
| Chapter digest (3.6) built late, "pays for itself if done before verification" | Chapter index + per-chapter summaries are **Phase 1 output** |
| Same fact stated in many files (redundancy audit 5.7) | One home per fact: entity files hold facts; topic files link. Redundancy report is part of lint |
| Stub character files expanded in three passes (2E.4, 2E.4b) | Entity completeness rule fixed up front (see 6) so files are written once |
| Heredoc scripts broke on apostrophes | Scripts are written as files and run |
| Spelling variants collected ad hoc (Hendren/Hedron...) | `ledgers/aliases.tsv` built *during* the reading pass; every variant has a canonical form |
| Open questions list grew organically | `ledgers/open_questions.md` appended during reading, each with cites; resolved before export |

## 3. Source hierarchy

1. **Book text** (`src/Source_Text/`, 19 e-books split into 510 files). Always wins.
2. **Author's notes** inside the e-books (Meta_ files): usable, cited as `(Book N, ChMeta_BNN_Authors_Note L..)`.
3. **Chapter notes** (`src/Chapter_Notes/`) are working summaries produced by the study pass. Anything important is re-confirmed against tier 1 before it enters an entry.
4. The lorebook/exports are **derived**, never cited, never a source.

No fan wiki is available or used. Where the books conflict, write what the text says at that point, record the disagreement in `open_questions.md`.

## 4. Layout

```
TWI_Compendium/
  00_Project_Structure.md   this file
  TODO_Build_Plan.md        phased plan with gates
  src/Source_Text/Book_01..19/   Ch_<seq>_<id>.txt  (+ Meta_ files)   NOT in git (copyright)
  src/Source_Text/README.md      generated chapter index
  src/Chapter_Notes/bNN.md       study-pass notes, one block per chapter
  src/ledgers/                   machine ledgers (names census, bracket catalog, aliases, entities, facts)
  src/tools/                     split.py check_split.py rd.py scan_*.py verify_*.py build_*.py ...
  src/exports/                   lorebook JSON + Markdown at chosen cutoffs (derived)
  01_World_Primer.md ... entity files (built after the study pass)
  Appendices/                    Glossary, Name_Index, Open_Questions, Change_Log, Source_Register
```

## 5. Chapter files

`Book_NN/Ch_<seq>_<id>.txt`. Line 1 is a header (`== Book N | id | heading | seq S ==`), line 2 onward one paragraph per line; blank lines removed; scene breaks normalised to `---`. **Cite = `(Book N, Ch<id> L<line>)`** using the physical line number, e.g. `(Book 6, Ch4.38B L212)`.

Ids: `N.NN` serial chapter (letter suffix = POV thread, e.g. `6.04D`; vol 1/2 suffixed series restart numbering by design), `Interlude_<Title>`, `Interlude_BNN_k` (author left untitled), `S0N_<Title>`, `Story_N_<Title>`, `Wistram_Days_Pt.N`, `Mating_Rituals_Pt.2`. `seq` is the global reading order 1-442 chapters + meta pages (510 files).

Verified: every volume's numbering is complete (1.00-1.45, 2.01-2.41, 3.00-3.42, 4.00-4.49, 5.00-5.62, 6.00-6.68, 7.00-7.55), TOC order equals detected order in all 11 books that have one, ids unique, 99.97% of source words placed.

## 6. Entity rules (decided now, not after)

- **Individual file / entry** for: any named character with a role in 2+ chapters or 15+ cited facts, every species, nation/city/region, organisation, class/skill/spell family, god/spirit/Name, notable item, event/war, and every concept the text explains.
- **Grouped file** only for named one-scene figures.
- Every entry has: canonical name, aliases (from `aliases.tsv`), type, `valid_from` (seq of first appearance), then atomic facts.

## 7. Fact record

One fact = one claim, one cite, one `seq`.
Fields: entity, kind (`fact` state/ability/appearance; `rel` relationship; `event`; `belief` in-world belief or lie; `reveal` identity/secret becomes known; `state` change such as death/class change/relocation), text, cite, seq. Spoiler cut at seq S = keep facts with seq ≤ S. A later correction is a new fact (`supersedes=`), never an edit of the earlier one.

## 8. Style rules

Prose present tense for how the world is, past tense for history. Full name on first use. Paraphrase; never reproduce chapter text beyond short voice quotes (under 15 words, cited). Distinguish fact, belief and rumour. Use the book's spellings and bracket convention for classes/skills ([Innkeeper], [Skill - X]).

## 9. Maintenance

`git commit` after each completed unit. Scripts are files. Re-run `scan_names.py` and `verify_notes.py` after each phase. Log every session in `Appendices/Change_Log.md`.
