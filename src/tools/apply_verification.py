"""Apply claim-verification decisions to entry files (Phase 3 verification pass).
Decision files: src/tools/cache/verify/*.tsv, tab-separated, header
  file  line  verdict  orig_prefix  new_bullet  note
verdict: OK | FIX | DROP.  FIX replaces the whole bullet with new_bullet (must end with a cite group);
DROP deletes the bullet.  orig_prefix = first 40 characters of the original claim text (after '- ');
a decision is skipped (and reported) if the line no longer starts with it.  Lines are applied bottom-up.
Run: python -I src/tools/apply_verification.py [--dry] [tag ...]   then lint_entities.py."""
import csv, glob, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CITE = re.compile(r"\(Book \d+, Ch\S+ L[\dL,\- ]+(?:; Book \d+, Ch\S+ L[\dL,\- ]+)*\)\s*$")
dry = "--dry" in sys.argv
dec = collections.defaultdict(list)
tags = [a for a in sys.argv[1:] if not a.startswith("--")]  # e.g. v04 v05 ; none = all decision files
for p in sorted(glob.glob(os.path.join(HERE, "cache", "verify", "*.tsv"))):
    if tags and os.path.splitext(os.path.basename(p))[0] not in tags:
        continue
    for r in csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="\t", quoting=csv.QUOTE_NONE):
        if r.get("verdict") in ("FIX", "DROP"):
            dec[r["file"]].append(r)
tot = collections.Counter()
for f, rows in dec.items():
    path = os.path.join(ROOT, f)
    lines = open(path, encoding="utf-8").read().split("\n")
    for r in sorted(rows, key=lambda r: -int(r["line"])):
        i = int(r["line"]) - 1
        cur = lines[i] if i < len(lines) else ""
        if not cur.startswith("- ") or not cur[2:].startswith(r["orig_prefix"]):
            print(f"SKIP {f}:{r['line']} (line changed): {cur[:60]}")
            tot["skipped"] += 1
            continue
        if r["verdict"] == "FIX":
            nb = r["new_bullet"].strip()
            if not nb.startswith("- "): nb = "- " + nb
            if not CITE.search(nb):
                print(f"SKIP {f}:{r['line']} new bullet has no cite"); tot["skipped"] += 1; continue
            lines[i] = nb
        else:
            del lines[i]
        tot[r["verdict"]] += 1
    if not dry:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(dict(tot), "(dry run)" if dry else "applied")
