"""Gate 1 coverage check: every census term with >= MIN occurrences must be covered.
Covered = the term (accent/case-insensitive) is, or is a whole-word part of, an entity name in a note line (text before
the first colon), a NEW: item, an alias/canonical in ledgers/aliases.tsv, or an entry in ledgers/stoplist.txt
(one term per line, '#' comments). Multi-word census terms are also covered when every word is covered separately
by some single entity/alias name.
Run: python -I src/tools/check_coverage.py [MIN=15]   Writes ledgers/coverage_gaps.tsv; exit 1 if gaps remain."""
import csv, glob, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..")
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 15

def norm(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s)
    s = re.sub(r"'s(?![a-z])", "", s)  # possessives: Erin's -> erin
    return re.sub(r"\s+", " ", s).strip()

names = set()
for p in glob.glob(os.path.join(SRC, "Chapter_Notes", "b[0-9][0-9].md")):
    for raw in open(p, encoding="utf-8-sig"):
        if raw[:2] in ("+ ", "~ ", "! "):
            names.add(norm(raw[2:].split(":", 1)[0]))
        elif raw.startswith("= "):
            for part in re.split(r"\s=\s", raw[2:].split("(")[0]): names.add(norm(part))
        elif raw.startswith("NEW:"):
            for it in raw[4:].split(","): names.add(norm(it))
with open(os.path.join(SRC, "ledgers", "aliases.tsv"), encoding="utf-8") as f:
    for r in csv.reader(f, delimiter="\t"):
        names.update(norm(x) for x in r[:2])
stop = set()
sp = os.path.join(SRC, "ledgers", "stoplist.txt")
if os.path.exists(sp):
    stop = {norm(l) for l in open(sp, encoding="utf-8") if l.strip() and not l.startswith("#")}
dp = os.path.join(SRC, "ledgers", "coverage_decisions.tsv")
if os.path.exists(dp):
    with open(dp, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="	"): stop.add(norm(r["term"]))
names.discard("")
words = set()
for n in names: words.update(re.findall(r"[a-z0-9']+", n))
joined = " | ".join(names)

LEAD = {"and", "but", "if", "then", "maybe", "or", "how", "hey", "now", "yes", "yeah", "you", "that", "the", "a", "an", "another",
        "every", "these", "those", "where", "when", "what", "so", "oh", "no", "why", "this", "not", "just", "at", "in", "of"}
CONTR = re.compile(r"^(i|you|he|she|we|they|it|that|there|what|who|let|here|where|how|can|don|won|didn|isn|wasn)('(ll|ve|d|m|re|s|t)|)$")

def covered(term):
    t = norm(term)
    if t in names or t in stop: return True
    ws = t.split()
    while ws and ws[0] in LEAD:
        ws = ws[1:]
    if not ws or (len(ws) == 1 and (CONTR.match(ws[0]) or ws[0] in LEAD)): return True
    t = " ".join(ws)
    if t in names or t in stop: return True
    if re.search(r"(?<![a-z0-9'])" + re.escape(t) + r"(?![a-z0-9'])", joined): return True
    ws = re.findall(r"[a-z0-9']+", t)
    return len(ws) > 1 and all(w in words or w in stop for w in ws)

gaps, total = [], 0
with open(os.path.join(SRC, "ledgers", "names_census.tsv"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if int(r["total"]) < MIN: continue
        total += 1
        if not covered(r["term"]): gaps.append((r["term"], r["total"], r["first_seq"], r["first_cite"]))
with open(os.path.join(SRC, "ledgers", "coverage_gaps.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\ttotal\tfirst_seq\tfirst_cite\n" + "\n".join("\t".join(g) for g in gaps) + "\n")
print(f"census terms >= {MIN}: {total}; uncovered: {len(gaps)} -> ledgers/coverage_gaps.tsv")
for g in gaps[:30]: print(" ", g[0], g[1], g[3])
sys.exit(1 if gaps else 0)
