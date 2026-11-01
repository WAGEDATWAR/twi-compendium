"""Phase 2.2: build entity-review work packages for agents (ledgers/work/ent_<pkg>.tsv).

Packages (by facts per entity, from entities.tsv + facts.jsonl):
  small  : entities with 1-2 facts          -> split into S slices
  mid    : 3-14 facts                        -> split into M slices
  big    : >= 15 facts (homonym + variant audit; rows carry book spread and census multi-token starters)
  manual : fact-less manual entities (needs_file=M) plus all alias rows of coverage_decisions_gap.tsv (decision review)
Each row carries: key, display, facts, forms, chapters, up to 3 sample facts with cites, and up to 6 candidate entities
(token overlap / near-spelling) so the reviewer can decide fold / split / topic / keep.
Run: python -I src/tools/make_entity_work.py"""
import collections, csv, difflib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")
os.makedirs(W, exist_ok=True)
S_SLICES, M_SLICES, B_SLICES, X_SLICES = 11, 3, 2, 2

E = {r["key"]: r for r in csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8"), delimiter="\t")}
F = collections.defaultdict(list)
for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8"):
    f = json.loads(l); F[f["key"]].append(f)
census = list(csv.DictReader(open(os.path.join(LED, "names_census.tsv"), encoding="utf-8"), delimiter="\t"))

tok = lambda k: [t for t in re.findall(r"[a-z0-9']+", k) if len(t) >= 3]
df = collections.Counter(t for k in E for t in set(tok(k)))
inv = collections.defaultdict(set)
for k in E:
    for t in set(tok(k)):
        if df[t] <= 60: inv[t].add(k)
nfacts = lambda k: int(E[k]["facts"])

def candidates(k, n=6):
    ts = set(tok(k)); sc = collections.Counter()
    for t in ts:
        for c in inv.get(t, ()):
            if c != k: sc[c] += 1 + (0.5 if len(t) > 5 else 0)
    for c in list(E):
        if c != k and abs(len(c) - len(k)) <= 3 and difflib.SequenceMatcher(None, c, k).ratio() >= 0.85: sc[c] += 2
    best = sorted(sc, key=lambda c: (-sc[c], -nfacts(c)))[:n]
    return " | ".join(f"{c} ({nfacts(c)})" for c in best)

def sample(k, n=3):
    out = []
    for f in F.get(k, [])[:n]:
        out.append(f"[{f['chapter']}] {f['marker']} {f['text'][:200]} {f['cite']}")
    return " || ".join(out).replace("\t", " ")

def row(k):
    e = E[k]; chs = sorted({f["chapter"] for f in F.get(k, [])})
    return [k, e["display"], e["facts"], e["forms"], ",".join(chs[:6]) + ("..." if len(chs) > 6 else ""), sample(k), candidates(k)]

HEAD = ["key", "display", "facts", "forms", "chapters", "sample_facts", "candidates"]
def dump(name, rows, head=HEAD):
    with open(os.path.join(W, name), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(head) + "\n")
        for r in rows: o.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")

small = sorted(k for k, e in E.items() if e["needs_file"] != "M" and int(e["facts"]) <= 2)
mid = sorted(k for k, e in E.items() if e["needs_file"] != "M" and 3 <= int(e["facts"]) < 15)
big = sorted((k for k, e in E.items() if e["needs_file"] != "M" and int(e["facts"]) >= 15), key=lambda k: -nfacts(k))
for i in range(S_SLICES): dump(f"ent_small_{i}.tsv", [row(k) for k in small[i::S_SLICES]])
for i in range(M_SLICES): dump(f"ent_mid_{i}.tsv", [row(k) for k in mid[i::M_SLICES]])

# big: add book spread and census multi-token starters (homonym signal)
starters = collections.defaultdict(list)
for r in census:
    ws = r["term"].split()
    if len(ws) >= 2 and int(r["total"]) >= 8:
        starters[ws[0].lower()].append((r["term"], int(r["total"]))); starters[ws[-1].lower()].append((r["term"], int(r["total"])))
def bigrow(k):
    spread = collections.Counter(f["book"] for f in F[k])
    st = sorted(starters.get(k, []), key=lambda x: -x[1])[:6] if " " not in k else []
    return row(k) + [" ".join(f"b{b}:{n}" for b, n in sorted(spread.items())), " | ".join(f"{t} ({n})" for t, n in st)]
for i in range(B_SLICES): dump(f"ent_big_{i}.tsv", [bigrow(k) for k in big[i::B_SLICES]], HEAD + ["book_spread", "census_multitoken"])

# manual entities + decision review rows
man = [k for k, e in E.items() if e["needs_file"] == "M"]
dec = list(csv.DictReader(open(os.path.join(LED, "coverage_decisions_gap.tsv"), encoding="utf-8"), delimiter="\t"))
mrows = []
for k in sorted(man): mrows.append(["ENTITY", k, E[k]["display"], "", candidates(k)])
for d in dec:
    if d["kind"] in ("alias", "stop"): mrows.append(["DECISION", d["term"], d["kind"], d["target"], d["note"][:160].replace("\t", " ")])
for i in range(X_SLICES): dump(f"ent_manual_{i}.tsv", mrows[i::X_SLICES], ["type", "key_or_term", "display_or_kind", "target", "candidates_or_note"])
print(f"small {len(small)} mid {len(mid)} big {len(big)} manual-rows {len(mrows)}")
