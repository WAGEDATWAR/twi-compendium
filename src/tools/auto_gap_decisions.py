"""Phase 2.3 helper: turn uncovered census terms into reviewable decisions where the answer is mechanical.
Reads ledgers/coverage_gaps.tsv (from check_coverage.py) and ledgers/entities.tsv; writes ledgers/coverage_decisions_auto.tsv.
Rule: after stripping honorifics, possessives and leading filler words, a single-token term that is the first or last token of
exactly ONE multi-word entity (>= 3 facts) becomes an `alias` row to that entity. Everything else is left for manual rows in
make_coverage_decisions.py. Run after check_coverage.py; re-run check_coverage.py afterwards."""
import csv, collections, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers")
sys.path.insert(0, HERE)
src = open(os.path.join(HERE, "check_coverage.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(HERE, "check_coverage.py")}
exec(compile(src.split("gaps, total = [], 0")[0].replace("sys.argv", "['x']"), "cc", "exec"), ns)
key, HONOR = ns["key"], ns["HONOR"]
ents = list(csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8"), delimiter="\t"))
first, last = collections.defaultdict(set), collections.defaultdict(set)
for r in ents:
    t = r["key"].split()
    if len(t) > 1 and int(r["facts"]) >= 3:
        first[t[0]].add(r["key"]); last[t[-1]].add(r["key"])
FILL = {"as", "because", "even", "is", "do", "well", "both", "more", "all", "other", "one", "their", "her", "in", "i'm", "im"}
EXCL = {"earth", "golem", "company", "macbeth", "silver", "spider", "levil", "lady atwood", "the golem", "earth's", "golem's"}
rows = []
for g in csv.DictReader(open(os.path.join(LED, "coverage_gaps.tsv"), encoding="utf-8"), delimiter="\t"):
    k = key(g["term"]); ws = k.split()
    while ws and (ws[0] in ns["LEAD"] or ws[0] in FILL): ws = ws[1:]
    k = " ".join(ws)
    changed = True
    while changed:
        changed = False
        for h in HONOR:
            if k.startswith(h): k = k[len(h):]; changed = True
    if len(k.split()) != 1 or len(k) < 4 or k in EXCL: continue
    c = first.get(k, set()) | last.get(k, set())
    if len(c) == 1: rows.append((g["term"], "alias", next(iter(c)), "auto: unique first/last-token match", g["first_cite"]))
with open(os.path.join(LED, "coverage_decisions_auto.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\tkind\ttarget\tnote\tfirst_cite\n" + "".join("\t".join(r) + "\n" for r in rows))
print(len(rows), "auto alias decisions")
