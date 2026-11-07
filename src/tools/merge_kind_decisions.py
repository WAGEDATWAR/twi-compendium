"""Phase 2.4: validate and merge the fact-kind reviews (ledgers/work/kind_out_K.tsv) into ledgers/fact_kinds.tsv.

kind_out rows are exceptions (wrong heuristic kind, or a supersession link); every other fact in the matching kind_in_K.tsv was
accepted as reviewed. fact_kinds.tsv therefore lists EVERY reviewed fact: sid, kind, supersedes (| separated), source, note.
Validation: sid exists in facts.jsonl; kind in the six kinds; each superseded sid exists, belongs to the same entity key and is
not later than the superseding fact. Failures go to ledgers/work/kind_rejected.tsv and the row falls back to the heuristic kind.
Run: python -I src/tools/merge_kind_decisions.py"""
import csv, glob, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")
KINDS = {"fact", "rel", "event", "belief", "reveal", "state"}
tsv = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t"))
F = {}
for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8"):
    f = json.loads(l); F[f["sid"]] = f
reviewed = {}
for p in sorted(glob.glob(os.path.join(W, "kind_in_*.tsv"))):
    out = p.replace("kind_in_", "kind_out_")
    if not os.path.exists(out): continue          # chunk not reviewed (yet): leave heuristic
    for r in tsv(p): reviewed[r["sid"]] = r["heuristic_kind"]
exc, rej = {}, []
for p in sorted(glob.glob(os.path.join(W, "kind_out_*.tsv"))):
    for r in tsv(p):
        s = (r.get("sid") or "").strip(); k = (r.get("kind") or "").strip().lower()
        sup = [x.strip() for x in (r.get("supersedes") or "").split("|") if x.strip()]
        why = None
        if s not in F: why = "unknown sid"
        elif k not in KINDS: why = "bad kind"
        else:
            for a in sup:
                if a not in F: why = "superseded sid unknown"; break
                if F[a]["key"] != F[s]["key"]: why = "superseded fact belongs to another entity"; break
                if (F[a]["seq"], F[a]["id"]) > (F[s]["seq"], F[s]["id"]) or a == s: why = "superseded fact is not earlier"; break
        if why: rej.append((os.path.basename(p), why, s, k, "|".join(sup)));
        if why and s in F and k in KINDS: exc[s] = (k, [], (r.get("note") or "").strip())      # keep a valid kind, drop bad links
        elif not why: exc[s] = (k, sup, (r.get("note") or "").strip())
rows, changed, links = [], 0, 0
for s, hk in reviewed.items():
    k, sup, note = exc.get(s, (hk, [], ""))
    if k != hk: changed += 1
    links += len(sup)
    rows.append((s, k, "|".join(sup), "reviewed", note))
with open(os.path.join(LED, "fact_kinds.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("sid\tkind\tsupersedes\tsource\tnote\n" + "".join("\t".join(x.replace("\t", " ") for x in r) + "\n" for r in rows))
with open(os.path.join(W, "kind_rejected.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("file\treason\tsid\tkind\tsupersedes\n" + "".join("\t".join(r) + "\n" for r in rej))
unrev = [s for s in F if s not in reviewed]
print(f"reviewed facts {len(rows)} of {len(F)} (unreviewed {len(unrev)}); kind changes {changed}; supersession links {links}; rejected rows {len(rej)}")
print("kinds:", dict(collections.Counter(r[1] for r in rows)))
