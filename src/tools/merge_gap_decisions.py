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
    s = s.strip(" '\"`")
    return re.sub(r"^(the|a|an) ", "", s)

ents = {r["key"] for r in csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8"), delimiter="\t")}
_am = {}
_ap = os.path.join(LED, "alias_map.tsv")
if os.path.exists(_ap):
    _am = {r["alias_key"]: r["canonical_key"] for r in csv.DictReader(open(_ap, encoding="utf-8"), delimiter="\t")}
def retarget(tg):
    "an alias target folded into another entity by review follows the fold"
    k = key(tg)
    return _am[k] if k not in ents and _am.get(k) in ents else k
KINDS = {"alias", "entity", "bracket", "stop", "ambiguous"}
good, bad, seen = [], [], set()
for p in sorted(glob.glob(os.path.join(LED, "gap_decisions_[0-9]*.tsv"))):
    for r in csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t"):
        t, k, tg = (r.get("term") or "").strip(), (r.get("kind") or "").strip().lower(), (r.get("target") or "").strip()
        why = None
        if not t or k not in KINDS: why = "bad term/kind"
        elif t in seen: why = "duplicate term"
        elif k == "alias" and retarget(tg) not in ents: why = "alias target not an entity key"
        elif k == "entity" and (not tg or not (r.get("etype") or "").strip()): why = "entity needs target and etype"
        elif k == "bracket" and not tg: why = "bracket needs target"
        elif k == "ambiguous" and (len([x for x in tg.split("|") if x.strip()]) < 2 or any(key(x) not in ents for x in tg.split("|") if x.strip())): why = "ambiguous needs 2+ existing entity keys separated by |"
        if why: bad.append((os.path.basename(p), why, t, k, tg)); continue
        seen.add(t)
        if k == "alias": tg = retarget(tg)
        good.append((t, k, tg, (r.get("etype") or "").strip(), (r.get("note") or "").strip(), (r.get("cite") or "").strip()))
# reviewed overrides (written by merge_entity_decisions.py from the manual-package DECISION rows): the override replaces the row
import csv as _csv
_op = os.path.join(LED, "gap_decision_overrides.tsv")
if os.path.exists(_op):
    ov = {r["term"]: r for r in _csv.DictReader(open(_op, encoding="utf-8-sig"), delimiter="	")}
    good = [g for g in good if g[0] not in ov] + [(t, r["kind"], r["target"], r["etype"], r["note"], "") for t, r in ov.items()]
with open(os.path.join(LED, "coverage_decisions_gap.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\tkind\ttarget\tetype\tnote\tfirst_cite\n")
    for g in good: o.write("\t".join(x.replace("\t", " ") for x in g) + "\n")
with open(os.path.join(LED, "gap_decisions_rejected.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("file\treason\tterm\tkind\ttarget\n" + "".join("\t".join(b) + "\n" for b in bad))
from collections import Counter
print(len(good), "merged;", len(bad), "rejected;", dict(Counter(g[1] for g in good)))
