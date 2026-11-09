"""Move entity files into the folder that matches the `> Type:` line their writer recorded (D-011).
  python -I src/tools/rehome_entities.py [--dry]
Only files in Entities/Other and files whose folder disagrees with their Type are moved (git mv).
Aborts without moving anything if two files would land on the same path. Updates cache/entities/manifest.tsv paths."""
import csv, os, re, subprocess, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DIR = {"person": "Characters", "place": "Places", "org": "Organisations", "organisation": "Organisations", "group": "Organisations",
       "item": "Items", "ship": "Items", "creature": "Creatures", "species": "Species", "concept": "Concepts",
       "class": "Classes", "skill": "Classes", "spell": "Spells", "title": "Titles", "event": "Events", "work": "Works"}
os.chdir(ROOT)
moves, seen = {}, set(glob.glob("Entities/*/*.md") + glob.glob("Entities/*/*/*.md"))
for f in sorted(glob.glob("Entities/*/*.md")):
    cur = f.split("/")[1]
    t = ""
    for l in open(f, encoding="utf-8"):
        m = re.match(r">\s*Type:\s*([^|]+)", l)
        if m: t = m.group(1).strip().lower(); break
    want = DIR.get(t)
    if not want or want == cur: continue
    if cur != "Other" and not (cur == "Titles" and t in ("person", "class")) and not (cur == "Items" and t == "ship" and False): continue
    moves[f] = f"Entities/{want}/{os.path.basename(f)}"
dest = list(moves.values())
clash = [d for d in set(dest) if dest.count(d) > 1 or (d in seen and d not in moves)]
if clash: sys.exit("collision, nothing moved: " + ", ".join(clash))
for a, b in moves.items():
    print(a, "->", b)
    if "--dry" in sys.argv: continue
    os.makedirs(os.path.dirname(b), exist_ok=True)
    subprocess.run(["git", "mv", a, b], check=True)
man = "src/tools/cache/entities/manifest.tsv"
if "--dry" not in sys.argv and os.path.exists(man):
    rows = list(csv.reader(open(man, encoding="utf-8"), delimiter="\t"))
    for r in rows[1:]:
        if r[5] in moves: r[5] = moves[r[5]]
    csv.writer(open(man, "w", encoding="utf-8", newline=""), delimiter="\t", lineterminator="\n").writerows(rows)
print(len(moves), "files", "(dry run)" if "--dry" in sys.argv else "moved")
