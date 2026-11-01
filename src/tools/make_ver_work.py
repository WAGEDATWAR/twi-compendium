"""Phase 2.2: build verification work files (ledgers/work/ver_in_K.tsv) for an independent second pass over the reviewed
folds, splits and homonym splits. Each row shows the alias key, the target key, the first reviewer's note, and sample facts for both
sides (from the pre-review snapshot facts_base_keys.tsv + current facts.jsonl). Verifiers answer ok / reject / uncertain."""
import csv, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")
tsv = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t"))
base = {r["sid"]: r["key"] for r in tsv(os.path.join(W, "facts_base_keys.tsv"))}
by = collections.defaultdict(list)
for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8"):
    f = json.loads(l); by[base.get(f["sid"].split("-")[0], f["key"])].append(f)
def smp(k, n=3):
    return " || ".join(f"[{f['chapter']}] {f['text'][:150]} {f['cite']}" for f in by.get(k, [])[:n]).replace("\t", " ")
rows = []
for r in tsv(os.path.join(LED, "alias_overrides.tsv")):
    if r["note"].startswith("2.2 review"):
        rows.append(["FOLD", r["alias"], r["canonical"], r["note"][:200], smp(r["alias"]), smp(r["canonical"])])
for r in tsv(os.path.join(LED, "entity_splits.tsv")):
    rows.append(["SPLIT", r["key"], r["targets"], r["note"][:200], smp(r["key"]), ""])
N = 8
for i in range(N):
    with open(os.path.join(W, f"ver_in_{i}.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("type\tkey\ttarget\treviewer_note\tkey_facts\ttarget_facts\n")
        for r in rows[i::N]: o.write("\t".join(r) + "\n")
print(len(rows), "rows in", N, "files")
