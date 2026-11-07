# TWI Compendium: Suggestions

Ideas beyond the current scope, awaiting triage. Ease: S/M/L. Status `proposed` until triaged; accepted ideas move into `TODO_Build_Plan.md` and the row is marked `accepted`.

| # | Idea | Ease | Best fit | Status |
|---|---|---|---|---|
| S-01 | Extend `verify_notes.py` to check numbers and `[bracket terms]` in a claim against the cited window, not just the entity name; most real errors are wrong numbers | S | Gate 1 | proposed |
| S-02 | `.gitattributes` (`* text=auto eol=lf`) to stop the CRLF warnings on every add | S | now | proposed |
| S-03 | One `tools/check_all.py` that runs split check, verify_notes, merge dry-run and the dangling-alias check, as a pre-commit gate | S | Gate 1 | proposed |
| S-04 | Rank `open_questions.md` by how many chapters/entities each touches so the load-bearing ones are resolved first | M | Phase 2 | proposed |
| S-05 | `extract_facts.py` that turns notes blocks straight into `facts.jsonl` (entity, kind from the `+ ~ ! =` marker, cite, seq) as a first Phase 2 draft | M | Phase 2 | proposed |
| S-06 | Auto-suggest alias canonicals from `names_census.tsv` plus the merged alias ledger to shrink DEF-005 | M | Phase 2 | proposed |
| S-07 | Run a second independent reader on a sample of ~30 chapters and diff its facts against the notes to estimate the miss rate | M | Phase 4 | proposed |
| S-08 | Export-time spoiler test: cut at every book boundary and assert no kept fact has `supersedes` pointing at a fact after the cut and no `reveal` fact precedes the belief it corrects | S | Phase 5 | proposed |
| S-09 | Auto-detect cross-piece supersession for big entities by matching `[Class] Level N` patterns across facts | M | Phase 3 | proposed |

