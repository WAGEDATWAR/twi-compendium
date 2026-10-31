"""Verify Chapter_Notes against Source_Text (plan item 0.7).
Checks per block: header id/seq match chapter_index.json; S: and NEW: lines present.
Per fact line (+ ~ ! =): has a (Lnn[-mm]) cite; cite within the chapter file; some token of the entity
name (text before the first colon) occurs within +-6 lines of the cite (accent/case-insensitive).
Run: python tools/verify_notes.py [--quiet]   Writes ledgers/verify_report.txt; exit 1 if hard errors."""
import glob, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..")
idx = {x["seq"]: x for x in json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]}
HDR = re.compile(r"^## (\S+) \| seq (\d+)")
CITE = re.compile(r"\(([^()]*\bL\d+[^()]*)\)\s*$")
CITES = re.compile(r"L(\d+)(?:-L?(\d+))?")
XREF = re.compile(r"\b\d\.\d\d[A-Z]*\b")
WIN = 6

def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

cache = {}
def lines(seq):
    if seq not in cache:
        p = os.path.join(SRC, "Source_Text", idx[seq]["file"].replace("\\", "/"))
        cache[seq] = [norm(l) for l in open(p, encoding="utf-8").read().split("\n")]
    return cache[seq]

def tokens(ent):
    ent = norm(re.sub(r"[\[\]]", " ", ent))
    return [t for t in re.findall(r"[a-z0-9']+", ent) if len(t) >= 3 and t not in {"the", "and", "his", "her", "its", "new", "all"}]

errs, warns, n_fact, n_block = [], [], 0, 0
for path in sorted(glob.glob(os.path.join(SRC, "Chapter_Notes", "b[0-9][0-9].md"))):
    cur = None
    def close():
        if cur and not cur["S"]:
            errs.append(f"{cur['tag']}: missing S: line")
        elif cur and not cur["NEW"]:
            warns.append(f"{cur['tag']}: missing NEW: line")
    for ln, raw in enumerate(open(path, encoding="utf-8-sig").read().split("\n"), 1):
        m = HDR.match(raw)
        if m:
            close()
            seq = int(m.group(2)); n_block += 1
            cur = {"tag": f"{os.path.basename(path)}:{ln} {m.group(1)}", "seq": seq, "S": False, "NEW": False}
            if seq not in idx: errs.append(f"{cur['tag']}: unknown seq {seq}"); cur = None
            elif idx[seq]["id"] != m.group(1): errs.append(f"{cur['tag']}: id != index id {idx[seq]['id']}")
            continue
        if not cur: continue
        if raw.startswith("S:"): cur["S"] = True
        elif raw.startswith("NEW:"): cur["NEW"] = True
        elif raw[:2] in ("+ ", "~ ", "! ", "= "):
            n_fact += 1
            c = CITE.search(raw)
            if not c: errs.append(f"{cur['tag']} line {ln}: no cite: {raw[:80]}"); continue
            if XREF.search(c.group(1)):
                warns.append(f"{cur['tag']} line {ln}: cross-chapter cite not checked: {raw[:70]}"); continue
            spans = [(int(a), int(b or a)) for a, b in CITES.findall(c.group(1))]
            L = lines(cur["seq"]); nl = len(L)
            if any(b > nl or a < 1 for a, b in spans):
                errs.append(f"{cur['tag']} line {ln}: cite beyond file ({nl} lines): {raw[:80]}"); continue
            ent = raw[2:].split(":", 1)[0] if raw[0] != "=" else raw[2:].split("=", 1)[0]
            toks = tokens(ent)
            if not toks: continue
            blob = " ".join(" ".join(L[max(0, a - 1 - WIN):min(nl, b + WIN)]) for a, b in spans)
            if not any(t in blob for t in toks):
                warns.append(f"{cur['tag']} line {ln}: '{ent.strip()}' not within +-{WIN} of cite: {raw[:70]}")
    close()
out = os.path.join(SRC, "ledgers", "verify_report.txt")
with open(out, "w", encoding="utf-8") as f:
    f.write(f"blocks {n_block}  fact lines {n_fact}  errors {len(errs)}  entity-warnings {len(warns)}\n\n== ERRORS ==\n" + "\n".join(errs) + "\n\n== ENTITY WARNINGS ==\n" + "\n".join(warns) + "\n")
print(f"blocks {n_block} facts {n_fact} errors {len(errs)} entity-warnings {len(warns)} ({100*len(warns)/max(1,n_fact):.1f}%) -> {out}")
for e in errs[:25]: print(e)
sys.exit(1 if errs else 0)
