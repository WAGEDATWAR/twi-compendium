"""Read and search chapter text with citation output.

  rd.py r  <id|seq> [lo [hi]]        print lines lo..hi of a chapter (default all), numbered as cited
  rd.py g  <regex> [book_from [book_to [max [width]]]]   grep every chapter; prints (Book N, Ch<id> L<line>) and the line
  rd.py ctx <id|seq> <line> [n]      n lines of context around a cited line
  rd.py ids [book]                   list chapter ids with seq

A chapter is addressed by its id (e.g. 6.04D, Interlude_Embria) or its global seq number.
Text is searched with typographic quotes normalised to ASCII so patterns can be typed plainly.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "src", "Source_Text")
IDX = json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]
BY_ID = {e["id"]: e for e in IDX}
BY_SEQ = {e["seq"]: e for e in IDX}
Q = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."})


def find(key):
    if key in BY_ID:
        return BY_ID[key]
    if key.isdigit() and int(key) in BY_SEQ:
        return BY_SEQ[int(key)]
    cands = [e for e in IDX if e["id"].lower() == key.lower() or key.lower() in e["id"].lower()]
    if len(cands) == 1:
        return cands[0]
    sys.exit("unknown or ambiguous chapter %r (%s)" % (key, ", ".join(c["id"] for c in cands[:6])))


def lines_of(e):
    return open(os.path.join(SRC, e["file"]), encoding="utf-8").read().split("\n")[:-1]


def cite(e, ln):
    return "(Book %d, Ch%s L%d)" % (e["book"], e["id"], ln)


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == "r":
        e = find(a[1])
        L = lines_of(e)
        lo = int(a[2]) if len(a) > 2 else 1
        hi = int(a[3]) if len(a) > 3 else len(L)
        for i in range(lo, min(hi, len(L)) + 1):
            print("%d\t%s" % (i, L[i - 1]))
    elif cmd == "ctx":
        e = find(a[1])
        L = lines_of(e)
        ln = int(a[2])
        n = int(a[3]) if len(a) > 3 else 3
        for i in range(max(1, ln - n), min(len(L), ln + n) + 1):
            print("%s%d\t%s" % (">" if i == ln else " ", i, L[i - 1]))
    elif cmd == "g":
        pat = re.compile(a[1], re.I)
        b0 = int(a[2]) if len(a) > 2 else 1
        b1 = int(a[3]) if len(a) > 3 else 19
        mx = int(a[4]) if len(a) > 4 else 60
        w = int(a[5]) if len(a) > 5 else 220
        shown = total = 0
        for e in IDX:
            if not (b0 <= e["book"] <= b1):
                continue
            for i, l in enumerate(lines_of(e), 1):
                t = l.translate(Q)
                m = pat.search(t)
                if m:
                    total += 1
                    if shown < mx:
                        s = max(0, m.start() - w // 2)
                        print("%s %s" % (cite(e, i), t[s:s + w]))
                        shown += 1
        print("-- %d matches (%d shown)" % (total, shown))
    elif cmd == "ids":
        for e in IDX:
            if len(a) < 2 or e["book"] == int(a[1]):
                print(e["seq"], e["id"], e["words"], e["lines"])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
