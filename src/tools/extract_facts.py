"""Phase 2.1: parse Chapter_Notes/bNN.md into ledgers/facts.jsonl and group facts by canonical entity.

One fact per `+ ~ ! =` line. Fields: id, entity_raw, entity (canonical display), key (canonical key), marker, kind, text,
cite (normalised "(Book N, Ch<id> L12-15)" list), lines (list of [a,b]), xref (cite names another chapter), seq, book, chapter.
Kind from the marker: + fact, ~ belief, ! state (reveal/state/event refined in 2.4), = alias (written to alias_pairs, not facts).
Canonicalisation: ledgers/aliases.tsv + alias rows of coverage_decisions.tsv, minus aliases listed in alias_conflicts.tsv and
minus ledgers/alias_overrides.tsv (manual resolutions: alias<TAB>canonical, wins over everything, empty canonical = never merge).
Outputs: ledgers/facts.jsonl, ledgers/entities.tsv, ledgers/entity_report.txt.
Run: python -I src/tools/extract_facts.py"""
import collections, csv, glob, hashlib, json, os, re, unicodedata
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
    s = s.strip(" '\"`")
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
override_targets = set(); protected = set()
for r in read_tsv("alias_overrides.tsv"):
    a, c = key(r["alias"]), key(r["canonical"])
    if c: amap[a] = c; override_targets.add(c)
    else: amap.pop(a, None); protected.add(a)   # never-merge: no later stage may map it
for c in override_targets:   # a reviewed canonical is terminal: it must not map elsewhere (avoids cycles)
    amap.pop(c, None)
# reviewed coverage decisions (ledgers/coverage_decisions_gap.tsv, written by merge_gap_decisions.py):
# alias rows fold the term into an existing entity; entity rows create a fact-less manual entity (filled in Phase 3).
manual = {}
for r in read_tsv("coverage_decisions.tsv"):      # first-round decisions (species, ranks...): entity rows also create entities
    if r["kind"] == "entity" and key(r["target"]):
        manual.setdefault(key(r["target"]), {"display": r["target"], "etype": "", "note": r.get("note", ""), "cite": r.get("first_cite", "")})
for r in read_tsv("coverage_decisions_gap.tsv"):
    a, c = key(r["term"]), key(r["target"])
    if r["kind"] == "alias" and c and a != c and a not in override_targets and a not in protected:
        amap[a] = c
    elif r["kind"] == "entity" and c:
        manual.setdefault(c, {"display": r["target"], "etype": r.get("etype", ""), "note": r.get("note", ""), "cite": r.get("first_cite", "")})
        if a != c and a not in override_targets and a not in protected: amap[a] = c

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
    if a and c and a != c and a not in amap and a not in conflicts and a not in protected:
        amap[a] = c; added_pairs += 1

def break_cycles():
    "Remove self-maps and break alias cycles: in each cycle the member with the most facts becomes terminal (keeps its own key)."
    cnt = collections.Counter(f["k0"] for f in facts)
    broken = 0
    for a in [a for a, c in amap.items() if a == c]: del amap[a]
    for a in sorted(amap):
        path, k = [], a
        while k in amap and k not in path:
            path.append(k); k = amap[k]
        if k in amap and k in path:                    # k is on a cycle
            cyc = path[path.index(k):]
            top = max(cyc, key=lambda x: (cnt[x], -len(x), x))
            amap.pop(top, None); broken += 1
    return broken
cycles_broken = break_cycles()

known = {canon(f["k0"]) for f in facts if not re.search(r" and | & ", f["k0"]) and "," not in f["k0"]}
SPLIT = re.compile(r"\s+and\s+|\s*&\s*|\s*,\s*")
expanded, joint = [], 0
for f in facts:
    parts = [p for p in SPLIT.split(f["k0"]) if p] if SPLIT.search(f["k0"]) else []
    ck = [canon(key(p)) for p in parts]
    if len(parts) >= 2 and all(c in known for c in ck) and len(set(ck)) == len(ck):
        for c in ck:
            g = dict(f); g["part"] = c; g["k0"] = c; g["joint_with"] = [x for x in ck if x != c]; expanded.append(g)
        joint += 1
    else:
        expanded.append(f)
facts = expanded
for f in facts:   # stable fact id: independent of alias decisions (joint parts hash their raw part key)
    f["sid"] = hashlib.sha1(("%s|%s|%s|%s" % (f["seq"], f["entity_raw"], f["text"], f.get("part", ""))).encode("utf-8")).hexdigest()[:10]
    f.pop("part", None)
for f in facts:
    f["key"] = canon(f["k0"])
# reviewed per-fact reassignment (homonym splits): ledgers/fact_entity_overrides.tsv  sid -> key, display
fo = {r["sid"]: r for r in read_tsv("fact_entity_overrides.tsv")}
ent_display = collections.defaultdict(collections.Counter)
for f in facts:
    if f["sid"] in fo:
        f["key"] = fo[f["sid"]]["key"]; f["entity_raw"] = fo[f["sid"]].get("display") or f["entity_raw"]
# reviewed composite splits: ledgers/entity_splits.tsv  key -> target|target ; the fact is copied to every target
spl = {r["key"]: [x for x in r["targets"].split("|") if x] for r in read_tsv("entity_splits.tsv")}
out_facts, split_n = [], 0
for f in facts:
    if f["key"] in spl and f["sid"] not in fo:
        ts = list(dict.fromkeys(canon(t) for t in spl[f["key"]])); split_n += 1   # targets folded together collapse to one
        if len(ts) == 1:
            g = dict(f); g["key"] = ts[0]; out_facts.append(g); continue
        for t in ts:
            g = dict(f); g["key"] = t; g["joint_with"] = [x for x in ts if x != t]; g["sid"] = f["sid"] + "-" + str(ts.index(t)); out_facts.append(g)
    else:
        out_facts.append(f)
facts = out_facts
for f in facts:
    ent_display[f["key"]][f["entity_raw"] if "joint_with" not in f else f["key"].title()] += 1
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

meta = {r["key"]: r for r in read_tsv("entity_meta.tsv")}   # reviewed etype / keep|topic decisions

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
    o.write("key\tdisplay\tfacts\tchapters\tfirst_seq\tbooks\tforms\taliases_known\tneeds_file\tetype\treview\n")
    for k, d in rows:
        nf = d["n"] >= 15 or len(d["chs"]) >= 2
        o.write("\t".join([k, ent_display[k].most_common(1)[0][0], str(d["n"]), str(len(d["chs"])), str(d["first"]),
                           ",".join(map(str, sorted(d["books"]))), "|".join(x for x, _ in d["raw"].most_common(6)),
                           "|".join(sorted(rev.get(k, ()))[:8]), "Y" if nf else "n",
                           meta.get(k, {}).get("etype", ""), meta.get(k, {}).get("decision", "")]) + "\n")
    written_manual = set()
    for k0, m in sorted(manual.items()):   # fact-less manual entities from coverage decisions (to be filled in Phase 3)
        k = canon(k0)                      # a manual entity folded into another entity by review is not created
        if k in E or k in written_manual: continue
        written_manual.add(k)
        o.write("\t".join([k, m["display"], "0", "0", "", "", m["display"], "|".join(sorted(rev.get(k, ()))[:8]), "M",
                           meta.get(k, {}).get("etype") or m.get("etype", ""), meta.get(k, {}).get("decision", "")]) + "\n")
nmanual = len(written_manual)
ne = len(rows); nfile = sum(1 for k, d in rows if d["n"] >= 15 or len(d["chs"]) >= 2)
single = sum(1 for k, d in rows if d["n"] == 1)
rep = [f"joint-subject facts split across entities: {joint}", f"facts {len(facts)}  alias pairs from '=' lines {len(pairs)} (new mappings {added_pairs})  xref-cite facts {sum(f['xref'] for f in facts)}  facts without cite {sum(1 for f in facts if not f['cite'])}",
       f"entities (canonical keys) {ne}; needing a file (>=15 facts or 2+ chapters) {nfile}; single-fact entities {single}",
       f"manual fact-less entities (from coverage decisions, needs_file=M): {nmanual}",
       f"alias map size {len(amap)}; conflicted aliases left unmerged {len(conflicts)}", "", "Top 40 entities:"]
rep += [f"  {d['n']:5d}  {len(d['chs']):3d} ch  {ent_display[k].most_common(1)[0][0]}" for k, d in rows[:40]]
open(os.path.join(LED, "entity_report.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(rep) + "\n")
print("\n".join(rep[:3]))
