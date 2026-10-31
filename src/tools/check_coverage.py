"""Gate 1/2 coverage check, strict (Phase 2.3): every census term with >= MIN occurrences must RESOLVE to something real.
A term is covered when, after dropping leading function words and possessives, its key is
  - a canonical entity key in ledgers/entities.tsv, or an alias key in ledgers/alias_map.tsv (which resolves to an entity), or
  - a row of ledgers/coverage_decisions.tsv: kind alias (target resolves to an entity), entity (target must itself exist in
    entities.tsv, i.e. the entity has been created), bracket (listed in ledgers/bracket_terms_all.tsv), stop (reason recorded), or
  - in ledgers/stoplist.txt, or a bare contraction/function word.
Run: python -I src/tools/check_coverage.py [MIN=15]   Writes ledgers/coverage_gaps.tsv; exit 1 if gaps remain.
(extract_facts.py must have been run first: it writes entities.tsv and alias_map.tsv.)"""
import csv, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers")
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 15
sys.path.insert(0, HERE)

def key(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s)
    s = re.sub(r"'s(?![a-z])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)

def tsv(name):
    p = os.path.join(LED, name)
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t")) if os.path.exists(p) else []

ents = {r["key"] for r in tsv("entities.tsv")}
amap = {r["alias_key"]: r["canonical_key"] for r in tsv("alias_map.tsv")}
brackets = {key(r["term"]) for r in tsv("bracket_terms_all.tsv")}
stop = set()
sp = os.path.join(LED, "stoplist.txt")
if os.path.exists(sp): stop = {key(l) for l in open(sp, encoding="utf-8") if l.strip() and not l.startswith("#")}
dec = {key(r["term"]): r for r in tsv("coverage_decisions_auto.tsv") + tsv("coverage_decisions.tsv") + tsv("coverage_decisions_gap.tsv")}
LEAD = {"and", "but", "if", "then", "maybe", "or", "how", "hey", "now", "yes", "yeah", "you", "that", "the", "a", "an", "another",
        "as", "because", "even", "is", "do", "well", "both", "more", "all", "other", "one", "their", "her", "i'm", "every", "these", "those", "where", "when", "what", "so", "oh", "no", "why", "this", "not", "just", "at", "in", "of"}
CONTR = re.compile(r"^(i|you|he|she|we|they|it|that|there|what|who|let|here|where|how|can|don|won|didn|isn|wasn)('(ll|ve|d|m|re|s|t)|)$")

HONOR = ("miss ", "mister ", "mr ", "sir ", "ser ", "lord ", "lady ", "captain ", "commander ", "senior guardsman ", "watch captain ",
         "revalantor ", "wall lord ", "magus ", "councilmember ", "general ", "king ", "queen ", "emperor ", "empress ", "witch ",
         "professor ", "master ", "strategist ", "councilwoman ", "warden ", "huntress ", "knight-commander ", "innkeeper ", "senior guardswoman ", "guardsman ", "desk sergeant ", "chief warrior ", "magus-crafter ", "grand mage ", "high king ", "dame ", "archmage ", "guildmaster ", "prognugator ", "grand ", "chieftain ", "bastion-general ")

def variants(k):
    out = [k]
    for h in HONOR:                       # strip stacked honorifics
        if k.startswith(h): out += variants(k[len(h):])
    if k.endswith("s"): out.append(k[:-1])
    if k.endswith("es"): out.append(k[:-2])
    out.append(k + "s")
    return out

def resolves(k):
    return any(v in ents or (v in amap and amap[v] in ents) for v in variants(k))

def covered(term):
    k0 = key(term)
    ws = k0.split()
    while ws and ws[0] in LEAD: ws = ws[1:]
    if not ws or (len(ws) == 1 and (CONTR.match(ws[0]) or ws[0] in LEAD)): return True
    k = " ".join(ws)
    if resolves(k) or resolves(k0) or k in stop or k0 in stop: return True
    d = dec.get(k0) or dec.get(k)
    if d:
        if d["kind"] == "stop": return True
        if d["kind"] == "bracket": return key(d["target"]) in brackets or k in brackets
        t = key(d["target"])
        return resolves(t)          # alias and entity rows both require the target to exist in the ledger
    return k in brackets

gaps, total = [], 0
for r in tsv("names_census.tsv"):
    if int(r["total"]) < MIN: continue
    total += 1
    if not covered(r["term"]): gaps.append((r["term"], r["total"], r["first_seq"], r["first_cite"]))
with open(os.path.join(LED, "coverage_gaps.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\ttotal\tfirst_seq\tfirst_cite\n" + "\n".join("\t".join(g) for g in gaps) + "\n")
print(f"census terms >= {MIN}: {total}; uncovered: {len(gaps)} -> ledgers/coverage_gaps.tsv")
sys.exit(1 if gaps else 0)
