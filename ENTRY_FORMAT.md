# Entry format (Phase 3)

Applies to every compendium file: root `NN_*.md` topic files and `Entities/**/*.md`. Checked by `python -I src/tools/lint_entities.py`.

## Shape

```
# Title
> Scope: one line saying what this file covers and what lives elsewhere.
> Keys: ledger entity keys this file draws on (optional).

## Section
- Claim in one sentence. (Book 3, Ch1.00D L12-14)
- {belief} In-world claim, rumour or lie, stated as such. (Book 2, Ch2.05 L40)
- Claim built from two places. (Book 1, Ch1.03 L40; Book 4, Ch3.12 L8,L22-23)
```

## Rules

1. **Every claim is one bullet ending in a cite group.** Prose paragraphs are not allowed except the `> Scope` line and section headings. No cite, no claim. A bullet must sit on one line.
2. **Cite = lines you actually read.** `(Book N, Ch<id> Lnn[-mm][,Lnn])`, the physical line in the chapter file (`python -I src/tools/rd.py r <id> lo hi`). Several places: separate groups with `; `. Cite the narrowest lines that support the claim, not a whole chapter.
3. **Spoiler cut = the latest chapter cited.** The lint derives each claim's `seq` as the highest seq among its cites, so a claim that needs a late reveal must cite it. Never state a later fact in an earlier claim's wording.
4. **Optional kind tag** at the start of the bullet: `{fact}` (default, may be omitted), `{rel}`, `{event}`, `{belief}`, `{reveal}`, `{state}`. Use `{belief}` for rumour, propaganda, in-world theory and anything a character merely asserts; `{reveal}` when the claim is a secret or identity becoming known; `{state}` for a change (death, class change, move).
5. **Retcons and change over time are separate claims**, ordered by seq, each with its own cite. Say what changed ("Later, ..."), never edit the earlier claim.
6. **Paraphrase.** Quotes only for short voice lines (under 15 words) inside double quotes. Numbers, levels and names exactly as the text gives them; no invented mechanics or values.
7. **Style.** Present tense for how the world is, past tense for history. Full name on first use in a section. Use the books' spelling and bracket convention: [Innkeeper], [Skill - X]. One home per fact: link to the other file in a `See:` heading note instead of repeating a claim.
8. **Open points** go to `src/ledgers/open_questions_*.md` style notes or the agent's hand-off file, not into claims.

## What the lint checks

Errors (block): bullet without a cite, unknown chapter, line outside the file, unknown `{kind}`.
Warnings (review): a number, a "quoted phrase" or a [Bracket Term] in the claim that does not occur within +-2 lines of its cites.
`--emit` writes `src/ledgers/entry_claims.jsonl` (file, section, kind, text, cites, seq) for the Phase 4 checks and the Phase 5 export.
