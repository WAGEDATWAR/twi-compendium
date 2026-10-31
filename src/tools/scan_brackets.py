"""Deterministic catalog of the bracketed game-text in the books: [Class], [Skill - X obtained!], [Spell - X], [Level N!], [Condition - X].

Writes src/ledgers/brackets.tsv  (kind, term, first_seq, first_cite, count, books) and src/ledgers/level_events.tsv
(every "[<Class> Level N!]" and "[<Class> obtained]" style line with cite, for tracking who levels when).
These are mechanical facts of the setting (classes, skills, spells, conditions) and need no judgement to extract.
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

SKILL = re.compile(r"\[(Skill|Spell|Condition|Skill Change|Class Change|Spell Change)\s*[–—-]\s*([^\]–—]+?)\s*(?:obtained|learned|acquired|lost)?!?\]")
LEVEL = re.compile(r"\[([A-Z][A-Za-z' \-]+?)\s+Level\s+(\d+)!?\]")
CLASSOBT = re.compile(r"\[([A-Z][A-Za-z' \-]+?)\s+(?:Class\s+)?(?:obtained|acquired)!?\]")
ANY = re.compile(r"\[([A-Z][^\[\]\n]{2,40})\]")

cat = defaultdict(lambda: {"first": None, "count": 0, "books": set()})
events = []
anyb = defaultdict(lambda: {"first": None, "count": 0, "books": set()})
for e in IDX:
    for i, l in enumerate(open(os.path.join(SRC, e["file"]), encoding="utf-8").read().split("\n")[:-1], 1):
        c = "(Book %d, Ch%s L%d)" % (e["book"], e["id"], i)
        for m in SKILL.finditer(l):
            k = (m.group(1), m.group(2).strip())
            d = cat[k]
            d["count"] += 1
            d["books"].add(e["book"])
            if d["first"] is None:
                d["first"] = (e["seq"], c)
            events.append(("skill", e["seq"], c, m.group(1), m.group(2).strip()))
        for m in LEVEL.finditer(l):
            events.append(("level", e["seq"], c, m.group(1).strip(), m.group(2)))
            k = ("Class", m.group(1).strip())
            d = cat[k]
            d["count"] += 1
            d["books"].add(e["book"])
            if d["first"] is None:
                d["first"] = (e["seq"], c)
        for m in CLASSOBT.finditer(l):
            events.append(("class", e["seq"], c, m.group(1).strip(), ""))
        for m in ANY.finditer(l):
            t = m.group(1).strip()
            d = anyb[t]
            d["count"] += 1
            d["books"].add(e["book"])
            if d["first"] is None:
                d["first"] = (e["seq"], c)

with open(os.path.join(LED, "brackets.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("kind\tterm\tfirst_seq\tfirst_cite\tcount\tbooks\n")
    for (k, t), d in sorted(cat.items(), key=lambda x: (x[1]["first"][0], x[0])):
        f.write("%s\t%s\t%d\t%s\t%d\t%s\n" % (k, t, d["first"][0], d["first"][1], d["count"], ",".join(map(str, sorted(d["books"])))))
with open(os.path.join(LED, "level_events.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("event\tseq\tcite\tname_or_class\tvalue\n")
    for ev in events:
        f.write("\t".join(map(str, ev)) + "\n")
with open(os.path.join(LED, "bracket_terms_all.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("term\tfirst_seq\tfirst_cite\tcount\tbooks\n")
    for t, d in sorted(anyb.items(), key=lambda x: (x[1]["first"][0], x[0])):
        f.write("%s\t%d\t%s\t%d\t%s\n" % (t, d["first"][0], d["first"][1], d["count"], ",".join(map(str, sorted(d["books"])))))
print("catalog rows: %d  events: %d  all bracket terms: %d" % (len(cat), len(events), len(anyb)))
