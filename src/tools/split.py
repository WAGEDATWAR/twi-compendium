"""Split the 19 Wandering Inn e-book text files into one file per chapter.

Input : BOOKS_DIR/bN.txt          (the raw e-book text, N = 1..19)
Output: src/Source_Text/Book_NN/Ch_<seq>_<id>.txt   one file per chapter / interlude / side story
        src/Source_Text/Book_NN/Meta_<seq>_<name>.txt author's notes, acknowledgements, note to readers
        src/tools/chapter_index.json                 machine index (seq, book, id, kind, words, lines, file ...)
        src/Source_Text/README.md                    human index

Chapter file format (so that every cite "(Book N, ChID LY)" is a physical line number):
  line 1      = header   "== Book N | <id> | <heading as printed> | seq <seq> =="
  line 2..    = one paragraph per line, blank lines removed, scene breaks normalised to "---"
Run: python3 src/tools/split.py [BOOKS_DIR]
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BOOKS_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/twi/books"
OUT = os.path.join(ROOT, "src", "Source_Text")

NUM = re.compile(r"^(\d+)\.(\d+)(?: ([A-Z]{1,3}))?$")
INTER = re.compile(r"^(?:Interlude|INTERLUDE)\b.{0,90}$")
SIDE = re.compile(r"^(?:S\d\d\s*[-–—]|Mini Stories|Story #\d|Wistram Days|Mating Rituals)")
META = re.compile(r"^(Author.s Note|Note to Readers|Acknowledg\w+|About the Author|More from the Innverse|Further Readin\w*|Copyright Notice)\s*:?$")
FRONT = re.compile(r"^(Contents|Table of Contents|Volume \d+|The Wandering Inn, Book \d+|BOOK \d+.*)$")
WATERMARK = re.compile(r"OceanofPDF\.com", re.I)
SCENEBREAK = re.compile(r"^[\s\-‐-―_*~=•.]{2,}$")
MIN_REAL_WORDS = 150


def classify(s):
    if NUM.match(s):
        return "chapter"
    if INTER.match(s):
        return "interlude"
    if SIDE.match(s):
        return "side"
    if META.match(s):
        return "meta"
    if FRONT.match(s):
        return "front"
    return None


def slug(s, maxlen=60):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\[|\]", "", s)
    s = re.sub(r"[^A-Za-z0-9.]+", "_", s).strip("_.")
    return s[:maxlen].strip("_") or "x"


def words(lines):
    return sum(len(x.split()) for x in lines)


def clean_line(l):
    l = l.replace(" ", " ").replace("​", "").replace("﻿", "").replace("­", "")
    l = l.rstrip("\r").strip()
    return l


def make_id(kind, heading, book, counters):
    m = NUM.match(heading)
    if m:
        return "%s.%s%s" % (m.group(1), m.group(2), m.group(3) or "")
    if kind == "interlude":
        t = re.sub(r"^(?:Interlude|INTERLUDE)\s*[-–—:]*\s*", "", heading).strip()
        if not t:
            counters[book] = counters.get(book, 0) + 1
            return "Interlude_B%02d_%d" % (book, counters[book])
        return "Interlude_" + slug(t)
    return slug(heading)


def split_book(n, entries, seq_start):
    raw = open(os.path.join(BOOKS_DIR, "b%d.txt" % n), encoding="utf-8").read().split("\n")
    lines = [clean_line(l) for l in raw]
    heads = []
    for i, s in enumerate(lines):
        if not s or len(s) > 100 or WATERMARK.search(s):
            continue
        k = classify(s)
        if k:
            heads.append((i, s, k))
    segs = []
    for j, (i, s, k) in enumerate(heads):
        end = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        body = [x for x in lines[i + 1:end] if x and not WATERMARK.search(x)]
        segs.append({"start": i + 1, "heading": s, "kind": k, "body": body, "words": words(body)})
    real, toc = [], []
    for sg in segs:
        if sg["kind"] in ("chapter", "interlude", "side"):
            (real if sg["words"] >= MIN_REAL_WORDS else toc).append(sg)
        elif sg["kind"] == "meta":
            (real if sg["words"] > 0 else toc).append(sg)
        else:
            toc.append(sg)
    group_of = {}
    for j, sg in enumerate(segs):
        if sg["kind"] in ("interlude", "side") and sg["words"] < MIN_REAL_WORDS and j + 1 < len(segs) and segs[j + 1]["kind"] in ("interlude", "side", "chapter"):
            group_of[segs[j + 1]["start"]] = sg["heading"]
    # sanity: inline watermark strings inside body lines
    inline = sum(1 for sg in real for x in sg["body"] if WATERMARK.search(x))
    counters = {}
    seq = seq_start
    bdir = os.path.join(OUT, "Book_%02d" % n)
    os.makedirs(bdir, exist_ok=True)
    for sg in real:
        body = []
        for x in sg["body"]:
            if SCENEBREAK.match(x):
                body.append("---")
            else:
                body.append(x)
        if sg["kind"] == "meta":
            name = slug(sg["heading"])
            ident = "Meta_B%02d_%s" % (n, name)
            fn = "Meta_%04d_%s.txt" % (seq, name)
            seq_used = seq
        else:
            ident = make_id(sg["kind"], sg["heading"], n, counters)
            seq += 0
            fn = "Ch_%04d_%s.txt" % (seq, slug(ident, 80))
            seq_used = seq
        header = "== Book %d | %s | %s | seq %d ==" % (n, ident, sg["heading"], seq_used)
        with open(os.path.join(bdir, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(header + "\n" + "\n".join(body) + "\n")
        m = NUM.match(sg["heading"])
        entries.append({
            "seq": seq_used, "book": n, "id": ident, "kind": sg["kind"], "heading": sg["heading"],
            "pov_tag": (m.group(3) if m and m.group(3) else ""), "serial_label": (("%s.%s" % (m.group(1), m.group(2))) if m else ""),
            "file": "Book_%02d/%s" % (n, fn), "words": words(body), "lines": len(body) + 1, "src_line": sg["start"],
            "title": "", "group": group_of.get(sg["start"], ""),
        })
        seq += 1
    return seq, {"book": n, "src_lines": len(lines), "heads": len(heads), "real": len(real), "toc_or_front": len(toc),
                 "inline_watermarks": inline, "src_words": words([x for x in lines if x and not WATERMARK.search(x)]),
                 "kept_words": sum(sg["words"] for sg in real), "toc_headings": [t["heading"] for t in toc if t["kind"] in ("chapter", "interlude", "side")]}


def write_readme(entries, stats):
    out = ["# Source_Text index", "",
           "One file per chapter, generated by `src/tools/split.py` from the 19 e-book text files. Not committed to git (copyright).", "",
           "Cite as `(Book N, Ch<id> L<line>)`; the line is the physical line in the chapter file (line 1 is the header, line 2 the first paragraph).",
           "Ids: `N.NN` = serial chapter, a letter suffix is the POV thread (e.g. `6.04D`); `Interlude_<title>`; `S0N_...` = side stories; `Story_N_...`.",
           "Bare interludes the author left untitled are `Interlude_BNN_k`; their working titles are in `chapter_index.json` (`title`).", ""]
    for st in stats:
        n = st["book"]
        out.append("## Book %d (%d files, %s words)" % (n, len([e for e in entries if e["book"] == n]), format(st["kept_words"], ",")))
        out.append("")
        out.append("| seq | id | heading | kind | words | lines | file |")
        out.append("|---|---|---|---|---|---|---|")
        for e in entries:
            if e["book"] == n:
                out.append("| %d | %s | %s | %s | %d | %d | %s |" % (e["seq"], e["id"], e["heading"], e["kind"], e["words"], e["lines"], e["file"].split("/")[1]))
        out.append("")
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def main():
    entries, stats, seq = [], [], 1
    for n in range(1, 20):
        seq, st = split_book(n, entries, seq)
        stats.append(st)
    with open(os.path.join(HERE, "chapter_index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"entries": entries, "stats": stats}, f, ensure_ascii=False, indent=1)
    write_readme(entries, stats)
    print("books: %d  files: %d" % (len(stats), len(entries)))
    for st in stats:
        lost = st["src_words"] - st["kept_words"]
        print("b%-2d real=%-3d dropped_headings=%-3d src_words=%-8d kept=%-8d not_in_chapters=%-6d inline_wm=%d" % (
            st["book"], st["real"], st["toc_or_front"], st["src_words"], st["kept_words"], lost, st["inline_watermarks"]))


if __name__ == "__main__":
    main()
