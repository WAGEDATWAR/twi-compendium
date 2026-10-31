# Chapter note format (parseable)

One block per chapter, in reading order, in `bNN.md` (NN = e-book number).

```
## <id> | seq <S> | POV: <who> | Where: <place> | When: <time marker as stated>
S: 2-4 sentence summary of what happens (past tense, no quotes).
+ Name: atomic fact (L12)
+ Name: atomic fact (L40-43)
~ Name: in-world belief / claim / lie / rumour, not established fact (L77)
! Name: reveal or state change (identity revealed, death, class/level change, relocation, relationship change) (L130)
= Alias A = Canonical Name (L9)           (alias / spelling-variant / title equivalence)
? open question or apparent contradiction with earlier text (L51)
NEW: terms first appearing in this chapter, comma separated (people, places, species, classes, items)
```

Rules
- Every `+ ~ ! =` line ends with a cite `(Lnn)` or `(Lnn-mm)`: physical line numbers in the chapter file. Lines without a cite are not facts.
- Entity name before the colon is the canonical form where known; otherwise the form used in the text.
- One claim per line. No mechanics invented; numbers only as stated.
- Keep a block to roughly 1.5-3 KB (about 3 percent of the chapter). Prefer concrete detail (names, places, numbers, ranks, levels, relationships, abilities) over mood.
- `When:` uses only what the text states (a season, "Day N", a holiday, a stated duration); otherwise `?`.
