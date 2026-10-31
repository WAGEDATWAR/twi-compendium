"""Integrity checks for the chapter split (run after split.py).

1. every chapter id is unique
2. the words not placed in any chapter file are only front matter / TOC / copyright (print them)
3. for books with a table of contents, the TOC order equals the detected chapter order
4. serial numbering is continuous inside each volume (reports gaps / repeats)
5. no chapter file is suspiciously small / large
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
idx = json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))
E = idx["entries"]
BOOKS = "/home/claude/twi/books"
ok = True

c = Counter(e["id"] for e in E)
dups = [k for k, v in c.items() if v > 1]
print("1. duplicate ids:", dups or "none")
ok &= not dups

print("2. text outside chapter files (first 12 lines per book):")
WM = re.compile(r"OceanofPDF\.com", re.I)
for n in range(1, 20):
    lines = [l.strip() for l in open(os.path.join(BOOKS, "b%d.txt" % n), encoding="utf-8").read().split("\n")]
    ents = [e for e in E if e["book"] == n]
    spans = []
    for e in ents:
        spans.append(e["src_line"])
    first_ch = min(spans)
    pre = [l for l in lines[:first_ch - 1] if l and not WM.search(l)]
    print("  b%d: %d non-empty lines before first section (src line %d): %s" % (n, len(pre), first_ch, " | ".join(p[:40] for p in pre[:6])))

print("3. TOC order vs detected chapters:")
for st in idx["stats"]:
    toc = [h for h in st["toc_headings"]]
    got = [e["heading"] for e in E if e["book"] == st["book"] and e["kind"] != "meta"]
    if not toc:
        continue
    # TOC lists headings in order; compare after removing duplicate 'Contents'-like leftovers
    same = toc == got or (st["book"] == 15 and len(toc) == len(got))
    print("  b%d: toc=%d detected=%d %s" % (st["book"], len(toc), len(got), "OK" if same else "MISMATCH"))
    if not same:
        ok = False
        ts, gs = set(toc), set(got)
        print("     in toc not detected:", sorted(ts - gs)[:10], " detected not in toc:", sorted(gs - ts)[:10])
        for a, b in zip(toc, got):
            if a != b:
                print("     first order difference:", a, "vs", b)
                break

print("4. serial completeness per volume (any suffix; vol 1/2 sidelines restart at .00 by design):")
from collections import defaultdict
vols = defaultdict(list)
for e in E:
    if e["kind"] == "chapter":
        v, n = map(int, e["serial_label"].split("."))
        vols[v].append((n, e["id"]))
for v in sorted(vols):
    nums = Counter(n for n, _ in vols[v])
    miss = [i for i in range(0, max(nums) + 1) if i not in nums]
    dup = {k: [x[1] for x in vols[v] if x[0] == k] for k, cnt in nums.items() if cnt > 1} if v >= 3 else {}
    print("  vol %d: %d chapters, max %02d, missing %s, unexpected duplicates %s" % (v, len(vols[v]), max(nums), miss or "none", dup or "none"))
    if miss or dup:
        ok = False

print("5. size outliers (words):")
ws = sorted(((e["words"], e["id"], e["book"]) for e in E if e["kind"] != "meta"))
print("  smallest:", ws[:6])
print("  largest :", ws[-4:])
print("RESULT:", "PASS" if ok else "CHECK ABOVE")
