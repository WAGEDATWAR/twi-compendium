"""Phase 2.3: merge the reviewed gap decisions (ledgers/gap_decisions_K.tsv, written by classification agents) into
ledgers/coverage_decisions_gap.tsv, validating every row.
Checks: kind in alias|entity|bracket|stop; alias target is an existing key in entities.tsv; entity rows carry a display name and
etype; each term appears once. Rows failing a check are written to ledgers/gap_decisions_rejected.tsv for rework, not merged.
Pipeline after this: extract_facts.py (creates manual entities, folds aliases) -> check_coverage.py.
Run: python -I src/tools/merge_gap_decisions.py"""
import csv, glob, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers")

def key(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s)
    s = re.sub(r"'s(?![a-z])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)

ents = {r["key"] for r in csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8"), delimiter="\t")}
KINDS = {"alias", "entity", "bracket", "stop"}
good, bad, seen = [], [], set()
for p in sorted(glob.glob(os.path.join(LED, "gap_decisions_[0-9]*.tsv"))):
    for r in csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t"):
        t, k, tg = (r.get("term") or "").strip(), (r.get("kind") or "").strip().lower(), (r.get("target") or "").strip()
        why = None
        if not t or k not in KINDS: why = "bad term/kind"
        elif t in seen: why = "duplicate term"
        elif k == "alias" and key(tg) not in ents: why = "alias target not an entity key"
        elif k == "entity" and (not tg or not (r.get("etype") or "").strip()): why = "entity needs target and etype"
        elif k == "bracket" and not tg: why = "bracket needs target"
        if why: bad.append((os.path.basename(p), why, t, k, tg)); continue
        seen.add(t)
        good.append((t, k, tg, (r.get("etype") or "").strip(), (r.get("note") or "").strip(), (r.get("cite") or "").strip()))
with open(os.path.join(LED, "coverage_decisions_gap.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\tkind\ttarget\tetype\tnote\tfirst_cite\n")
    for g in good: o.write("\t".join(x.replace("\t", " ") for x in g) + "\n")
with open(os.path.join(LED, "gap_decisions_rejected.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("file\treason\tterm\tkind\ttarget\n" + "".join("\t".join(b) + "\n" for b in bad))
from collections import Counter
print(len(good), "merged;", len(bad), "rejected;", dict(Counter(g[1] for g in good)))
