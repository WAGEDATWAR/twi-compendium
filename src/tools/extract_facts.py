"""Phase 2.1: parse Chapter_Notes/bNN.md into ledgers/facts.jsonl and group facts by canonical entity.

One fact per `+ ~ ! =` line. Fields: id, entity_raw, entity (canonical display), key (canonical key), marker, kind, text,
cite (normalised "(Book N, Ch<id> L12-15)" list), lines (list of [a,b]), xref (cite names another chapter), seq, book, chapter.
Kind from the marker: + fact, ~ belief, ! state (reveal/state/event refined in 2.4), = alias (written to alias_pairs, not facts).
Canonicalisation: ledgers/aliases.tsv + alias rows of coverage_decisions.tsv, minus aliases listed in alias_conflicts.tsv and
minus ledgers/alias_overrides.tsv (manual resolutions: alias<TAB>canonical, wins over everything, empty canonical = never merge).
Outputs: ledgers/facts.jsonl, ledgers/entities.tsv, ledgers/entity_report.txt.
Run: python -I src/tools/extract_facts.py"""
import collections, csv, glob, json, os, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..")
LED = os.path.join(SRC, "ledgers")
idx = {x["seq"]: x for x in json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]}

def key(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s)
    s = re.sub(r"'s(?![a-z])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)

def read_tsv(name):
    p = os.path.join(LED, name)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))

# ---- alias map -------------------------------------------------------------
conflicts = {key(r["alias"]) for r in read_tsv("alias_conflicts.tsv")}
amap = {}
for r in read_tsv("aliases.tsv"):
    a, c = key(r["alias"]), key(r["canonical"])
    if a and c and a != c and a not in conflicts: amap[a] = c
for r in read_tsv("coverage_decisions.tsv"):
    if r["kind"] == "alias" and r["target"]: amap[key(r["term"])] = key(r["target"])
override_targets = set()
for r in read_tsv("alias_overrides.tsv"):
    a, c = key(r["alias"]), key(r["canonical"])
    if c: amap[a] = c; override_targets.add(c)
    else: amap.pop(a, None); conflicts.discard(a)
for c in override_targets:   # a reviewed canonical is terminal: it must not map elsewhere (avoids cycles)
    amap.pop(c, None)
# reviewed coverage decisions (ledgers/coverage_decisions_gap.tsv, written by merge_gap_decisions.py):
# alias rows fold the term into an existing entity; entity rows create a fact-less manual entity (filled in Phase 3).
manual = {}
for r in read_tsv("coverage_decisions_gap.tsv"):
    a, c = key(r["term"]), key(r["target"])
    if r["kind"] == "alias" and c and a != c and a not in override_targets:
        amap[a] = c
    elif r["kind"] == "entity" and c:
        manual.setdefault(c, {"display": r["target"], "etype": r.get("etype", ""), "note": r.get("note", ""), "cite": r.get("first_cite", "")})
        if a != c and a not in override_targets: amap[a] = c

def canon(k):
    seen = set()
    while k in amap and k not in seen:
        seen.add(k); k = amap[k]
    return k

# ---- parse -----------------------------------------------------------------
HDR = re.compile(r"^## (\S+) \| seq (\d+)")
CITE = re.compile(r"\(([^()]*\bL\d+[^()]*)\)\s*$")
SPAN = re.compile(r"L(\d+)(?:-L?(\d+))?")
XREF = re.compile(r"\b\d\.\d\d[A-Z]*\b")

REVEAL = re.compile(r"\b(reveal|revealed|reveals|identity|true name|turns out|is actually|is really|learns? that|secretly|disguis|alias)", re.I)
STATE = re.compile(r"\b(dies|died|death|killed|dead|slain|class|level|levels|reaches|gains?|gained|becomes?|became|promoted|joins?|joined|leaves|left|captured|freed|wakes|awake|arrives?|relocat|moves? to|returns?|loses?|lost|destroyed|burned|crowned)\b", re.I)
REL = re.compile(r"^(friends?|enem(y|ies)|allies|ally|mother|father|sister|brother|daughter|son|wife|husband|married|owner|employer|employs|serves?|member of|leader of|rival|lover|mentor|student|apprentice|ward|child|children|parents?|cousin|uncle|aunt|niece|nephew|girlfriend|boyfriend|partner|siblings?)\b", re.I)

def classify(mk, text):
    "Heuristic fact kind (refined in review): + fact|rel, ~ belief, ! reveal|state|event."
    if mk == "~": return "belief"
    if mk == "!":
        return "reveal" if REVEAL.search(text) else ("state" if STATE.search(text) else "event")
    return "rel" if REL.match(text) else "fact"

facts, pairs = [], []
display = collections.defaultdict(collections.Counter)
for path in sorted(glob.glob(os.path.join(SRC, "Chapter_Notes", "b[0-9][0-9].md"))):
    seq = None
    for raw in open(path, encoding="utf-8-sig").read().split("\n"):
        m = HDR.match(raw)
        if m: seq = int(m.group(2)); continue
        if seq is None or raw[:2] not in ("+ ", "~ ", "! ", "= "): continue
        mk, body = raw[0], raw[2:]
        c = CITE.search(body)
        spans, xref = [], False
        if c:
            xref = bool(XREF.search(c.group(1)))
            spans = [[int(a), int(b or a)] for a, b in SPAN.findall(c.group(1))]
            body = body[:c.start()].rstrip()
        e = idx[seq]
        cite = "(Book %d, Ch%s %s)" % (e["book"], e["id"], ",".join("L%d" % a if a == b else "L%d-%d" % (a, b) for a, b in spans)) if spans else ""
        if mk == "=":
            parts = [p.strip() for p in re.split(r"\s=\s", body)]
            if len(parts) >= 2: pairs.append({"alias": parts[0], "canonical": parts[1], "cite": cite, "seq": seq})
            continue
        ent, _, text = body.partition(":")
        ent, text = ent.strip(), text.strip()
        k = key(ent)
        if not k or not text: continue
        display[k][ent] += 1
        facts.append({"entity_raw": ent, "k0": k, "marker": mk, "kind": classify(mk, text), "kind_source": "heuristic",
                      "text": text, "cite": cite, "lines": spans, "xref": xref, "seq": seq, "book": e["book"], "chapter": e["id"]})

# alias pairs from `=` lines also feed the map (only where the alias is not conflicted and not already mapped)
added_pairs = 0
for p in pairs:
    a, c = key(p["alias"]), key(p["canonical"])
    if a and c and a != c and a not in amap and a not in conflicts:
        amap[a] = c; added_pairs += 1

known = {canon(f["k0"]) for f in facts if not re.search(r" and | & ", f["k0"]) and "," not in f["k0"]}
SPLIT = re.compile(r"\s+and\s+|\s*&\s*|\s*,\s*")
expanded, joint = [], 0
for f in facts:
    parts = [p for p in SPLIT.split(f["k0"]) if p] if SPLIT.search(f["k0"]) else []
    ck = [canon(key(p)) for p in parts]
    if len(parts) >= 2 and all(c in known for c in ck) and len(set(ck)) == len(ck):
        for c in ck:
            g = dict(f); g["k0"] = c; g["joint_with"] = [x for x in ck if x != c]; expanded.append(g)
        joint += 1
    else:
        expanded.append(f)
facts = expanded
ent_display = collections.defaultdict(collections.Counter)
for f in facts:
    k = canon(f["k0"]); f["key"] = k
    ent_display[k][f["entity_raw"] if "joint_with" not in f else f["k0"].title()] += 1
for f in facts:
    f["entity"] = ent_display[f["key"]].most_common(1)[0][0]
for i, f in enumerate(facts, 1):
    f["id"] = "F%05d" % i
    del f["k0"]
with open(os.path.join(LED, "facts.jsonl"), "w", encoding="utf-8", newline="\n") as o:
    for f in facts: o.write(json.dumps(f, ensure_ascii=False) + "\n")

with open(os.path.join(LED, "alias_map.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("alias_key\tcanonical_key\n")
    for a in sorted(amap): o.write(f"{a}\t{canon(a)}\n")

# ---- entities --------------------------------------------------------------
E = collections.defaultdict(lambda: {"n": 0, "chs": set(), "first": 10**9, "books": set(), "raw": collections.Counter(), "kinds": collections.Counter()})
for f in facts:
    d = E[f["key"]]
    d["n"] += 1; d["chs"].add(f["seq"]); d["first"] = min(d["first"], f["seq"]); d["books"].add(f["book"])
    d["raw"][f["entity_raw"]] += 1; d["kinds"][f["kind"]] += 1
rev = collections.defaultdict(set)
for a, c in amap.items(): rev[canon(c)].add(a)
rows = sorted(E.items(), key=lambda kv: (-kv[1]["n"], kv[0]))
with open(os.path.join(LED, "entities.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("key\tdisplay\tfacts\tchapters\tfirst_seq\tbooks\tforms\taliases_known\tneeds_file\n")
    for k, d in rows:
        nf = d["n"] >= 15 or len(d["chs"]) >= 2
        o.write("\t".join([k, ent_display[k].most_common(1)[0][0], str(d["n"]), str(len(d["chs"])), str(d["first"]),
                           ",".join(map(str, sorted(d["books"]))), "|".join(x for x, _ in d["raw"].most_common(6)),
                           "|".join(sorted(rev.get(k, ()))[:8]), "Y" if nf else "n"]) + "\n")
    for k, m in sorted(manual.items()):   # fact-less manual entities from coverage decisions (to be filled in Phase 3)
        if k in E: continue
        o.write("\t".join([k, m["display"], "0", "0", "", "", m["display"], "|".join(sorted(rev.get(k, ()))[:8]), "M"]) + "\n")
nmanual = sum(1 for k in manual if k not in E)
ne = len(rows); nfile = sum(1 for k, d in rows if d["n"] >= 15 or len(d["chs"]) >= 2)
single = sum(1 for k, d in rows if d["n"] == 1)
rep = [f"joint-subject facts split across entities: {joint}", f"facts {len(facts)}  alias pairs from '=' lines {len(pairs)} (new mappings {added_pairs})  xref-cite facts {sum(f['xref'] for f in facts)}  facts without cite {sum(1 for f in facts if not f['cite'])}",
       f"entities (canonical keys) {ne}; needing a file (>=15 facts or 2+ chapters) {nfile}; single-fact entities {single}",
       f"manual fact-less entities (from coverage decisions, needs_file=M): {nmanual}",
       f"alias map size {len(amap)}; conflicted aliases left unmerged {len(conflicts)}", "", "Top 40 entities:"]
rep += [f"  {d['n']:5d}  {len(d['chs']):3d} ch  {ent_display[k].most_common(1)[0][0]}" for k, d in rows[:40]]
open(os.path.join(LED, "entity_report.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(rep) + "\n")
print("\n".join(rep[:3]))
