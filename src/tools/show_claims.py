"""Show entry-file claims next to the text they cite, for verification.
  python -I src/tools/show_claims.py <file.md> [first_line [last_line]]
For every bullet claim in the line range prints: file line number, the claim, then each cited span
(+-1 line of context, cited lines marked '>'), so a verifier can judge claim vs text in one call."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IDX = {(e["book"], e["id"]): e for e in json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]}
TAIL = re.compile(r"\(((?:Book \d+, Ch\S+ L[\dL,\- ]+)(?:; Book \d+, Ch\S+ L[\dL,\- ]+)*)\)\s*$")
ONE = re.compile(r"Book (\d+), Ch(\S+) (L[\dL,\- ]+)")
SPAN = re.compile(r"L?(\d+)(?:-L?(\d+))?")
path = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
for ln, raw in enumerate(open(path, encoding="utf-8-sig").read().split("\n"), 1):
    if ln < lo or ln > hi or not raw.startswith("- "):
        continue
    m = TAIL.search(raw)
    print(f"\n#{ln} {raw[2:]}")
    if not m:
        print("   (no cite)")
        continue
    for b, cid, spec in ONE.findall(m.group(1)):
        e = IDX.get((int(b), cid))
        if not e:
            print(f"   !! unknown chapter {b} {cid}")
            continue
        L = open(os.path.join(ROOT, "src", "Source_Text", e["file"].replace("\\", "/")), encoding="utf-8").read().split("\n")[:-1]
        print(f"   -- Book {b} Ch{cid}")
        for a, z in [(int(a), int(z or a)) for a, z in SPAN.findall(spec)]:
            for i in range(max(1, a - 1), min(len(L), z + 1) + 1):
                mark = ">" if a <= i <= z else " "
                print(f"   {mark}{i}: {L[i-1][:600]}")
