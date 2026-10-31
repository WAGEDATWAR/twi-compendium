"""Merge Chapter_Notes/parts/bNN_pK.md into Chapter_Notes/bNN.md, ordered by seq.
Run: python tools/merge_notes.py   (idempotent: blocks are keyed by seq; part file wins on a duplicate)"""
import glob, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.join(HERE, "..", "Chapter_Notes")
HDR = re.compile(r"^## (\S+) \| seq (\d+)")

def blocks(path):
    out, cur = [], None
    for line in open(path, encoding="utf-8-sig").read().replace("\r\n", "\n").split("\n"):
        m = HDR.match(line)
        if m:
            cur = [int(m.group(2)), [line]]
            out.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return [(s, "\n".join(l).rstrip() + "\n") for s, l in out]

books = collections.defaultdict(dict)
for p in sorted(glob.glob(os.path.join(NOTES, "b[0-9][0-9].md")) + glob.glob(os.path.join(NOTES, "parts", "b*_p*.md"))):
    b = os.path.basename(p)[:3]
    for s, t in blocks(p):
        books[b][s] = t
for b, d in sorted(books.items()):
    with open(os.path.join(NOTES, b + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(d[s] for s in sorted(d)))
    print(b, len(d), "blocks, seq", min(d), "-", max(d))
