"""Phase 2.2 helper: suggest folding a short entity key into a longer one (Ryoka -> Ryoka Griffin, Ceria -> Ceria Springwalker).
A short key S (one token) is suggested for the long key L when L starts with S + space (first-name fold), L has >=3 facts,
and L is the ONLY multi-word entity starting with S (unique), or the top one holds >=80% of such facts (dominant).
Writes ledgers/fold_suggestions.tsv for review; nothing is applied until copied into ledgers/alias_overrides.tsv."""
import csv, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers")
rows = list(csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8"), delimiter="\t"))
n = {r["key"]: int(r["facts"]) for r in rows}
byfirst = collections.defaultdict(list)
for k in n:
    if " " in k: byfirst[k.split()[0]].append(k)
out = []
for s in n:
    if " " in s or s not in byfirst: continue
    cands = sorted(byfirst[s], key=lambda k: -n[k])
    top = cands[0]; tot = sum(n[c] for c in cands)
    if n[top] < 3: continue
    conf = "unique" if len(cands) == 1 else ("dominant" if n[top] >= 0.8 * tot else "ambiguous")
    out.append((s, top, n[s], n[top], conf, "|".join(cands[1:4])))
out.sort(key=lambda r: (r[4] != "unique", -(r[2] + r[3])))
with open(os.path.join(LED, "fold_suggestions.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("short\tlong\tshort_facts\tlong_facts\tconfidence\tother_candidates\n" + "\n".join("\t".join(map(str, r)) for r in out) + "\n")
print(collections.Counter(r[4] for r in out))
