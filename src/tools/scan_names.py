"""Census of capitalised names in the books (the lesson of the HWFWM build: do the missing-name scan FIRST, not last).

For every capitalised word or capitalised phrase that is NOT at the start of a sentence, count occurrences per book and record
the first appearance (seq + cite). Output: src/ledgers/names_census.tsv  (term, total, first_seq, first_cite, books, per-book counts)
Terms are single capitalised tokens and 2-3 token capitalised phrases (Erin Solstice, Lady Magnolia Reinhart, Wistram Academy).
This is a LEAD LIST for the reading pass and the final coverage check: every term above the threshold must end up in an entry,
the alias table or the stoplist (src/ledgers/stoplist.txt).
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "src", "Source_Text")
LED = os.path.join(ROOT, "src", "ledgers")
os.makedirs(LED, exist_ok=True)
IDX = json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]

CAP = r"[A-Z][a-zÀ-ſ'’]+(?:-[A-Z]?[a-z]+)*"
PHRASE = re.compile(r"\b(%s(?:\s+(?:of|the|de|du|von|van|al|el|bint|ibn|d')?\s*%s){0,3})\b" % (CAP, CAP))
SENT_START = re.compile(r"(^|[.!?…:]\s+|[\"“‘(\[\-—–]\s*)$")

tot = defaultdict(int)
first = {}
per = defaultdict(lambda: defaultdict(int))
for e in IDX:
    if e["kind"] == "meta":
        continue
    for i, line in enumerate(open(os.path.join(SRC, e["file"]), encoding="utf-8").read().split("\n")[1:-1] if False else open(os.path.join(SRC, e["file"]), encoding="utf-8").read().split("\n")[:-1], 1):
        if i == 1:
            continue
        for m in PHRASE.finditer(line):
            before = line[:m.start()]
            if SENT_START.search(before) or before.strip() == "":
                # sentence-initial: only count when the phrase has 2+ tokens (a real name) to avoid 'The', 'She'
                if " " not in m.group(1):
                    continue
            term = m.group(1).strip()
            tot[term] += 1
            per[term][e["book"]] += 1
            if term not in first:
                first[term] = (e["seq"], "(Book %d, Ch%s L%d)" % (e["book"], e["id"], i))

rows = sorted(tot.items(), key=lambda x: (-x[1], x[0]))
with open(os.path.join(LED, "names_census.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("term\ttotal\tfirst_seq\tfirst_cite\tbooks\tper_book\n")
    for t, n in rows:
        if n < 3:
            continue
        pb = per[t]
        f.write("%s\t%d\t%d\t%s\t%d\t%s\n" % (t, n, first[t][0], first[t][1], len(pb), ",".join("%d:%d" % (b, pb[b]) for b in sorted(pb))))
print("distinct terms: %d; with >=3 occurrences: %d; >=15: %d; >=50: %d" % (len(rows), sum(1 for _, n in rows if n >= 3), sum(1 for _, n in rows if n >= 15), sum(1 for _, n in rows if n >= 50)))
