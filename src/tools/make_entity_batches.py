"""Build entity-file work packets for Phase 3 (D-010/D-011).
  python -I src/tools/make_entity_batches.py <tag> <etype[,etype...]> [--max-facts N] [--min-facts M] [--skip-done]
Selects (and skips any already in manifest.tsv) ledger entities of those etypes that need a file (needs_file Y/M, or >=15 facts, or >=2 chapters),
orders them by first appearance, packs them into batches of at most N facts (default 260; an entity larger than N
gets a batch of its own; fact-less entities count as 8 facts) and writes, for each batch,
  src/tools/cache/entities/<tag>_NN.md       packet: per entity, its ledger facts as bullets (show_claims.py can display them)
and appends rows to src/tools/cache/entities/manifest.tsv (batch, key, display, etype, facts, target path).
Target path: Entities/<TypeDir>/<Slug>.md.  --skip-done leaves out entities whose target file already exists.
An entity with more than N facts is split into chronological parts (cut at chapter boundaries); each part is its own
batch and is written to Entities/<TypeDir>/<Slug>/Part_<k>_Books_<a>-<b>.md.
Packets are seeds: the writer must verify every claim against the chapter text."""
import csv, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LED = os.path.join(ROOT, "src", "ledgers")
OUT = os.path.join(HERE, "cache", "entities")
TYPEDIR = {"place": "Places", "org": "Organisations", "person": "Characters", "item": "Items", "event": "Events",
           "title": "Titles", "concept": "Concepts", "class": "Classes", "spell": "Spells", "other": "Other", "": "Other"}
args = [a for a in sys.argv[1:] if not a.startswith("--")]
tag, types = args[0], {"" if t == "none" else t for t in args[1].split(",")}  # "none" = entities without an etype
opt = lambda n, d: int(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d
MAXF, MINF = opt("--max-facts", 260), opt("--min-facts", 0)
ents = list(csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8-sig"), delimiter="\t"))
F = [json.loads(l) for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8")]
by, bysid = {}, {f["sid"]: f for f in F}
for f in F: by.setdefault(f["key"], []).append(f)

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s or "Unnamed"

sel = []
for r in ents:
    et = r["etype"] or ""
    if et not in types: continue
    nf, nc = int(r["facts"] or 0), int(r["chapters"] or 0)
    if not (r["needs_file"] in ("Y", "M") or nf >= 15 or nc >= 2) or nf < MINF: continue
    sel.append(r)
man_path = os.path.join(OUT, "manifest.tsv")
if os.path.exists(man_path):  # an entity already packed in an earlier batch (any tag) is never packed again
    have = {r["key"] for r in csv.DictReader(open(man_path, encoding="utf-8"), delimiter="\t")}
    sel = [r for r in sel if r["key"] not in have]
sel.sort(key=lambda r: (int(r["first_seq"] or 0), r["key"]))
used, rows = {}, []
for r in sel:
    d = TYPEDIR.get(r["etype"] or "", "Other"); s = slug(r["display"])
    p = f"Entities/{d}/{s}.md"
    if p in used: p = f"Entities/{d}/{s}_{slug(r['key'])}.md"
    used[p] = r["key"]
    r["_path"] = p
if "--skip-done" in sys.argv:
    sel = [r for r in sel if not os.path.exists(os.path.join(ROOT, r["_path"]))]
import math
parts = []  # (row, facts_subset or None, label) for oversized entities
def split_big(r):
    fs = sorted(by.get(r["key"], []), key=lambda f: (f["seq"], f["id"]))
    k = math.ceil(len(fs) / MAXF)
    target = len(fs) / k
    chunks, cur_c = [], []
    for f in fs:
        cur_c.append(f)
        if len(cur_c) >= target and len(chunks) < k - 1 and (not cur_c or True):
            chunks.append(cur_c); cur_c = []
    if cur_c: chunks.append(cur_c)
    # move chunk boundaries so a chapter is never cut in two
    for i in range(len(chunks) - 1):
        while chunks[i + 1] and chunks[i] and chunks[i][-1]["seq"] == chunks[i + 1][0]["seq"]:
            chunks[i].append(chunks[i + 1].pop(0))
    return [c for c in chunks if c]
exp = []
for r in sel:
    if int(r["facts"] or 0) > MAXF:
        ch = split_big(r)
        d, s_ = os.path.dirname(r["_path"]), os.path.splitext(os.path.basename(r["_path"]))[0]
        for i, c in enumerate(ch, 1):
            r2 = dict(r); a, z = c[0]["book"], c[-1]["book"]
            r2["_path"] = f"{d}/{s_}/Part_{i}_Books_{a}-{z}.md"
            r2["display"] = f"{r['display']} (part {i} of {len(ch)}: Books {a}-{z})"
            r2["facts"] = str(len(c)); r2["_facts"] = c; r2["_part"] = (i, len(ch))
            exp.append(r2)
    else:
        exp.append(r)
sel = exp
W0 = 8  # a fact-less (manual) entity must be researched in the text: count it as W0 facts when packing
batches, cur, n = [], [], 0
for r in sel:
    nf = max(int(r["facts"] or 0), W0)
    if cur and n + nf > MAXF:
        batches.append(cur); cur, n = [], 0
    cur.append(r); n += nf
    if nf > MAXF: batches.append(cur); cur, n = [], 0
if cur: batches.append(cur)
os.makedirs(OUT, exist_ok=True)
man = os.path.join(OUT, "manifest.tsv")
new = not os.path.exists(man)
mf = open(man, "a", encoding="utf-8", newline="")
if new: mf.write("batch\tkey\tdisplay\tetype\tfacts\tpath\n")
for i, b in enumerate(batches, 1):
    name = f"{tag}_{i:02d}"
    with open(os.path.join(OUT, name + ".md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# BATCH {name}\n\nEach `##` block is one entity. Bullets are ledger facts (seeds, NOT sources), in reading order.\n")
        for r in b:
            fs = r.get("_facts") or sorted(by.get(r["key"], []), key=lambda f: (f["seq"], f["id"]))
            fh.write(f"\n## ENTITY: {r['display']}\n")
            fh.write(f"<!-- key: {r['key']} | type: {r['etype'] or 'other'} | facts: {len(fs)} | chapters: {r['chapters']} | books: {r['books']} | write to: {r['_path']} -->\n")
            fh.write(f"<!-- also called: {(r['aliases_known'] or '').replace('|', '; ')} | raw forms: {(r['forms'] or '').replace('|', '; ')} -->\n")
            for f in fs:
                pre = "{%s} " % f["kind"]
                if f["entity_raw"].strip().lower() != r["display"].strip().lower():
                    pre += "[about: %s] " % f["entity_raw"]
                for sid in f.get("supersedes") or []:
                    o = bysid.get(sid)
                    if o: pre += "[replaces earlier: %s] " % o["text"][:60].replace("(", "[").replace(")", "]")
                fh.write(f"- {pre}{f['text']} {f['cite']}\n")
            mf.write("\t".join([name, r["key"], r["display"], r["etype"] or "other", str(len(fs)), r["_path"]]) + "\n")
    print(f"{name}: {len(b)} entities, {sum(int(r['facts'] or 0) for r in b)} facts, {sum(1 for r in b if not int(r['facts'] or 0))} fact-less")
mf.close()
