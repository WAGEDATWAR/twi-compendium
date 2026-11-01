"""Phase 2.2: verification work files for the OLD alias pairs (aliases.tsv + notes `=` lines) that were never independently checked.
Rows: every alias->canonical in ledgers/alias_map.tsv that is not a reviewed override (2.2 review / manual union / never-merge) and
whose alias has its own facts or a cite. Output ledgers/work/ver_in_a<K>.tsv (type ALIAS)."""
import collections, csv, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")
tsv = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t"))
def key(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s); s = re.sub(r"'s(?![a-z])", "", s); s = re.sub(r"\s+", " ", s).strip().strip(" '\"`")
    return re.sub(r"^(the|a|an) ", "", s)
reviewed = {key(r["alias"]) for r in tsv(os.path.join(LED, "alias_overrides.tsv"))}
reviewed |= {key(r["term"]) for r in tsv(os.path.join(LED, "coverage_decisions_gap.tsv"))}
reviewed |= {key(r["term"]) for r in tsv(os.path.join(LED, "coverage_decisions.tsv"))}
am = {r["alias_key"]: r["canonical_key"] for r in tsv(os.path.join(LED, "alias_map.tsv"))}
cites = collections.defaultdict(list)
for r in tsv(os.path.join(LED, "aliases.tsv")): cites[(key(r["alias"]), key(r["canonical"]))].append(r["cites"][:60])
raw = collections.defaultdict(list); tgt = collections.defaultdict(list)
for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8"):
    f = json.loads(l)
    raw[key(f["entity_raw"])].append(f); tgt[f["key"]].append(f)
smp = lambda fs, n=3: " || ".join(f"[{f['chapter']}] {f['text'][:140]} {f['cite']}" for f in fs[:n]).replace("\t", " ")
rows = []
for a, c in sorted(am.items()):
    if a in reviewed or a == c: continue
    canon = c
    while canon in am and am[canon] != canon and canon != a: canon = am[canon]
    rows.append(["ALIAS", a, canon, "; ".join(cites.get((a, c), []))[:150], smp(raw.get(a, [])), smp(tgt.get(canon, []))])
N = 12
for i in range(N):
    with open(os.path.join(W, f"ver_in_a{i}.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("type\tkey\ttarget\treviewer_note\tkey_facts\ttarget_facts\n")
        for r in rows[i::N]: o.write("\t".join(r) + "\n")
print(len(rows), "alias rows in", N, "files")
