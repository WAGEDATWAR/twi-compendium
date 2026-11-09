"""Lint Phase 3 entry files (see ENTRY_FORMAT.md).

Every bullet ("- ...") in an entry file is a claim and must end with a cite group:
    (Book N, Ch<id> Lnn[-mm][,Lnn...][; Book M, Ch<id> Lnn])
Errors (exit 1): bullet without cite, unknown chapter, line outside the file, bad {kind} tag.
Warnings: number, "quoted phrase" or [Bracket Term] in the claim not found within +-WIN lines of its cites.
The claim seq (spoiler cut) is the highest seq among its cites.

Run: python -I src/tools/lint_entities.py [--emit] [--quiet] [files...]
Default files: root NN_*.md (not 00_*) and Entities/**/*.md.  --emit writes ledgers/entry_claims.jsonl.
Report: ledgers/lint_entities_report.txt (default run) or tools/cache/lint_<file>.txt (explicit files)"""
import glob, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "src")
IDX = json.load(open(os.path.join(HERE, "chapter_index.json"), encoding="utf-8"))["entries"]
BY_ID = {(e["book"], e["id"]): e for e in IDX}
KINDS = {"fact", "rel", "event", "belief", "reveal", "state"}
WIN = 2

TAIL = re.compile(r"\(((?:Book \d+, Ch\S+ L[\dL,\- ]+)(?:; Book \d+, Ch\S+ L[\dL,\- ]+)*)\)\s*$")
ONE = re.compile(r"Book (\d+), Ch(\S+) (L[\dL,\- ]+)")
SPAN = re.compile(r"L?(\d+)(?:-L?(\d+))?")
KIND = re.compile(r"^\{(\w+)\}\s*")


def norm(s):
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."}))
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def squash(s):
    return re.sub(r"[^a-z0-9]+", " ", norm(s)).strip()


_cache = {}


def lines(e):
    if e["seq"] not in _cache:
        p = os.path.join(SRC, "Source_Text", e["file"].replace("\\", "/"))
        _cache[e["seq"]] = open(p, encoding="utf-8").read().split("\n")[:-1]
    return _cache[e["seq"]]


def lint(path, errs, warns, claims):
    rel = os.path.relpath(path, ROOT)
    head, fence = "", False
    for ln, raw in enumerate(open(path, encoding="utf-8-sig").read().split("\n"), 1):
        if raw.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if raw.startswith("#"):
            head = raw.lstrip("# ").strip()
            continue
        if not raw.lstrip().startswith("- "):
            continue
        text = raw.lstrip()[2:].strip()
        tag = f"{rel}:{ln}"
        m = TAIL.search(text)
        if not m:
            errs.append(f"{tag}: no cite at end: {text[:80]}")
            continue
        body = text[: m.start()].strip()
        kind = "fact"
        k = KIND.match(body)
        if k:
            kind = k.group(1)
            body = body[k.end():]
            if kind not in KINDS:
                errs.append(f"{tag}: unknown kind {{{kind}}}")
        cites, ok, spans_by_ch = [], True, []
        for b, cid, spec in ONE.findall(m.group(1)):
            e = BY_ID.get((int(b), cid))
            if not e:
                errs.append(f"{tag}: unknown chapter Book {b} Ch{cid}")
                ok = False
                continue
            spans = [(int(a), int(z or a)) for a, z in SPAN.findall(spec)]
            nl = len(lines(e))
            if any(z > nl or a < 1 or z < a for a, z in spans):
                errs.append(f"{tag}: cite beyond Ch{cid} ({nl} lines): L{spec}")
                ok = False
                continue
            cites.append({"book": int(b), "chapter": cid, "seq": e["seq"], "lines": spans})
            spans_by_ch.append((e, spans))
        if not ok:
            continue
        blobs = []
        for e, spans in spans_by_ch:
            L = lines(e)
            nl = len(L)
            blobs.append(" ".join(" ".join(L[max(0, a - 1 - WIN):min(nl, z + WIN)]) for a, z in spans))
        blob = " ".join(blobs)  # a claim is checked against all of its cites together
        nb, sb = norm(blob).replace(",", ""), squash(blob)
        miss = []
        nbody = re.sub(r"\b\d+(?:st|nd|rd|th)\b", " ", re.sub(r"\bBook \d+\b", " ", body))  # "Book 7" labels and ordinals ("5th Wall") are not claims about numbers
        for n in re.findall(r"\d[\d,]*", nbody):
            n = n.replace(",", "").strip()
            if n and not re.search(r"(?<!\d)%s(?!\d)" % re.escape(n), nb):
                miss.append(n)
        for q in re.findall(r"[“\"]([^”\"]{3,})[”\"]", body):
            if squash(q) not in sb:
                miss.append('"%s"' % q[:30])
        for br in re.findall(r"\[([^\]]{2,40})\]", body):
            b2 = squash(br)
            if b2 not in sb and not (b2.endswith("s") and b2[:-1] in sb):  # plural of a bracket term
                miss.append("[%s]" % br)
        if miss:
            warns.append(f"{tag}: {', '.join(e['id'] for e, _ in spans_by_ch)} window lacks {', '.join(miss)} :: {body[:70]}")
        claims.append({"file": rel, "line": ln, "section": head, "kind": kind, "text": body,
                       "cites": cites, "seq": max(c["seq"] for c in cites)})


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = args or sorted([f for f in glob.glob(os.path.join(ROOT, "[0-9][0-9]_*.md"))
                            if not os.path.basename(f).startswith("00_")] +
                           glob.glob(os.path.join(ROOT, "Entities", "**", "*.md"), recursive=True))
    errs, warns, claims = [], [], []
    for f in files:
        lint(f, errs, warns, claims)
    if args:  # explicit files: per-file report in the (gitignored) cache so parallel runs do not collide
        os.makedirs(os.path.join(HERE, "cache"), exist_ok=True)
        out = os.path.join(HERE, "cache", "lint_%s.txt" % os.path.splitext(os.path.basename(args[0]))[0])
    else:
        out = os.path.join(SRC, "ledgers", "lint_entities_report.txt")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"files {len(files)}  claims {len(claims)}  errors {len(errs)}  warnings {len(warns)}\n\n== ERRORS ==\n"
                 + "\n".join(errs) + "\n\n== WARNINGS ==\n" + "\n".join(warns) + "\n")
    if "--emit" in sys.argv:
        with open(os.path.join(SRC, "ledgers", "entry_claims.jsonl"), "w", encoding="utf-8") as fh:
            for c in claims:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"files {len(files)} claims {len(claims)} errors {len(errs)} warnings {len(warns)} -> {out}")
    if "--quiet" not in sys.argv:
        for e in errs[:200]:
            print("ERR ", e)
        for w in warns[:80]:
            print("WARN", w)
    sys.exit(1 if errs else 0)


main()
