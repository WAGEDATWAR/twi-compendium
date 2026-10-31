"""Merge per-book/per-part ledgers into ledgers/aliases.tsv and ledgers/open_questions.md.
aliases.tsv: canonical, alias, n_cites, cites (first 3, with source tag), books. Rows keyed on (canonical, alias), case-insensitive.
Aliases listed under different canonicals for the same alias are written to alias_conflicts.tsv for review.
Run: python tools/merge_ledgers.py"""
import collections, glob, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "..", "ledgers")
TAG = re.compile(r"aliases_(b\d\d(?:_p\d\d)?)\.tsv$")

rows = collections.OrderedDict()
bad = []
for p in sorted(glob.glob(os.path.join(LED, "aliases_b*.tsv"))):
    tag = TAG.search(p).group(1)
    for ln, raw in enumerate(open(p, encoding="utf-8-sig"), 1):
        raw = raw.rstrip("\r\n")
        if not raw.strip() or raw.startswith("#"): continue
        f = [x.strip() for x in raw.split("\t")]
        if len(f) < 2 or not f[0] or not f[1]:
            bad.append(f"{tag}:{ln}: {raw[:80]}"); continue
        cite = f[2] if len(f) > 2 else ""
        key = (f[0].casefold(), f[1].casefold())
        r = rows.setdefault(key, {"canon": f[0], "alias": f[1], "cites": [], "books": set()})
        r["cites"].append(f"{tag} {cite}".strip()); r["books"].add(tag[:3])
rows = {k: v for k, v in rows.items() if k[0] != k[1]}
by_alias = collections.defaultdict(set)
for (c, a), r in rows.items(): by_alias[a].add(r["canon"])
conf = {a: s for a, s in by_alias.items() if len(s) > 1}
with open(os.path.join(LED, "aliases.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("canonical\talias\tn\tcites\tbooks\n")
    for (c, a), r in sorted(rows.items()):
        o.write(f"{r['canon']}\t{r['alias']}\t{len(r['cites'])}\t{'; '.join(r['cites'][:3])}\t{','.join(sorted(r['books']))}\n")
with open(os.path.join(LED, "alias_conflicts.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("alias\tcanonicals\n")
    for a, s in sorted(conf.items()): o.write(f"{a}\t{' | '.join(sorted(s))}\n")
nq = 0
with open(os.path.join(LED, "open_questions.md"), "w", encoding="utf-8", newline="\n") as o:
    o.write("# Open questions (merged from per-book ledgers; resolve before export)\n")
    cur = None
    for p in sorted(glob.glob(os.path.join(LED, "open_questions_b*.md"))):
        tag = re.search(r"open_questions_(b\d\d(?:_p\d\d)?)", p).group(1)
        if tag[:3] != cur: cur = tag[:3]; o.write(f"\n## Book file {cur}\n\n")
        for raw in open(p, encoding="utf-8-sig"):
            raw = raw.rstrip()
            if raw.lstrip().startswith(("-", "*")) or re.match(r"\d+[.)] ", raw.lstrip()):
                o.write(f"{raw}  [{tag}]\n"); nq += 1
            elif raw and not raw.startswith("#"):
                o.write(f"{raw}  [{tag}]\n")
print(f"aliases {len(rows)} unique pairs, conflicts {len(conf)}, malformed {len(bad)}, open questions {nq}")
for b in bad[:10]: print(" bad", b)
