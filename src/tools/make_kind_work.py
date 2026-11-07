"""Phase 2.4: build fact-kind review work packages (ledgers/work/kind_in_K.tsv).

Facts are grouped by entity, ordered by seq, and packed into chunks of roughly CHUNK facts (an entity larger than BIG is cut into
consecutive pieces of BIG facts; supersession links are then only found within a piece). Each row:
  entity, sid, chapter, marker, heuristic_kind, text (<=230 chars)
Reviewers write only EXCEPTIONS to ledgers/work/kind_out_K.tsv: rows where the kind is wrong, or the fact supersedes earlier facts.
Run: python -I src/tools/make_kind_work.py"""
import collections, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")
CHUNK, BIG = 620, 330
F = [json.loads(l) for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8")]
by = collections.defaultdict(list)
for f in F: by[f["key"]].append(f)
pieces = []
for k in sorted(by, key=lambda k: -len(by[k])):
    fs = sorted(by[k], key=lambda f: (f["seq"], f["id"]))
    for i in range(0, len(fs), BIG): pieces.append((k, fs[i:i + BIG]))
chunks, cur, n = [], [], 0
for k, fs in pieces:                     # first-fit decreasing into chunks
    placed = False
    for c in chunks:
        if c[0] + len(fs) <= CHUNK: c[0] += len(fs); c[1].append((k, fs)); placed = True; break
    if not placed: chunks.append([len(fs), [(k, fs)]])
for i, (cnt, items) in enumerate(chunks):
    with open(os.path.join(W, f"kind_in_{i}.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("entity\tsid\tchapter\tmarker\theuristic_kind\ttext\n")
        for k, fs in sorted(items, key=lambda x: x[0]):
            for f in fs:
                o.write("\t".join([k, f["sid"], f["chapter"], f["marker"], f["kind"], f["text"][:230].replace("\t", " ").replace("\n", " ")]) + "\n")
print(len(F), "facts,", len(pieces), "entity pieces ->", len(chunks), "chunks of <=", CHUNK, [c[0] for c in chunks])
