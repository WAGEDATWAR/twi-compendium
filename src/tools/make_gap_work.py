"""Split ledgers/coverage_gaps.tsv into N work files (ledgers/gap_work_K.tsv) with a context snippet from the first cite."""
import csv, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, ".."); LED = os.path.join(SRC, "ledgers")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
rows = list(csv.DictReader(open(os.path.join(LED, "coverage_gaps.tsv"), encoding="utf-8"), delimiter="\t"))
for k in range(N):
    with open(os.path.join(LED, f"gap_work_{k}.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("term\ttotal\tfirst_cite\tcontext\n")
        for r in rows[k::N]:
            m = re.match(r"\(Book (\d+), Ch(\S+) L(\d+)\)", r["first_cite"])
            ctx = ""
            if m:
                b, i, l = m.groups()
                f = glob.glob(os.path.join(SRC, "Source_Text", "Book_%02d" % int(b), "Ch_*_%s.txt" % i))
                if f:
                    line = open(f[0], encoding="utf-8").read().split("\n")[int(l) - 1]
                    t = r["term"].split()[0]
                    j = max(0, line.find(t))
                    ctx = line[max(0, j - 100):j + 160].replace("\t", " ")
            o.write(f"{r['term']}\t{r['total']}\t{r['first_cite']}\t{ctx}\n")
print(len(rows), "terms split into", N)
