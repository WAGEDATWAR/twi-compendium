"""Phase 2.2: validate and apply the entity-review decisions (ledgers/work/dec_*.tsv).

Row decisions (key, decision, target, etype, note):
  fold   -> alias_overrides.tsv   (alias=key, canonical=target); rejected if target missing/self, key protected as never-merge,
            or it would create a cycle
  split  -> entity_splits.tsv     (key -> targets; every target must exist)
  topic / keep -> entity_meta.tsv (etype, decision, home)
  homonym -> fact_entity_overrides.tsv (sid -> new key) from target `newkey=sid,sid;newkey2=sid`
  manual package: ENTITY rows use fold/topic/keep as above; DECISION rows: ok | change_alias | change_stop | change_entity
  -> gap_decision_overrides.tsv (read by merge_gap_decisions.py)
Overrides previously written by this script (note starting '2.2 review') are regenerated each run. Rejected rows go to
ledgers/work/dec_rejected.tsv with a reason. Idempotent. After running: merge_gap_decisions.py, extract_facts.py, check_coverage.py.
Run: python -I src/tools/merge_entity_decisions.py"""
import collections, csv, glob, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); LED = os.path.join(HERE, "..", "ledgers"); W = os.path.join(LED, "work")

def key(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\[\]\"]", "", s)
    s = re.sub(r"'s(?![a-z])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(" '\"`")
    return re.sub(r"^(the|a|an) ", "", s)

def tsv(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig"), delimiter="\t")) if os.path.exists(path) else []
def write(path, head, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(head) + "\n" + "".join("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n" for r in rows))

# Decisions are validated against the FROZEN pre-review snapshot (work/entities_base.tsv, work/facts_base_keys.tsv),
# not the live ledger: applying folds shrinks entities.tsv, so validating live would reject on the second run (not idempotent).
ents = {r["key"]: r for r in tsv(os.path.join(W, "entities_base.tsv"))}
sid_key = {r["sid"]: r["key"] for r in tsv(os.path.join(W, "facts_base_keys.tsv"))}
TAG = "2.2 review"
ov_path = os.path.join(LED, "alias_overrides.tsv")
ov = [r for r in tsv(ov_path) if not r["note"].startswith(TAG)]
protected = {key(r["alias"]) for r in ov if not r["canonical"]}          # never-merge rows
chain = {key(r["alias"]): key(r["canonical"]) for r in ov if r["canonical"]}

def reaches(a, c):                      # would a -> c create a cycle?
    seen = set()
    while c in chain and c not in seen:
        if c == a: return True
        seen.add(c); c = chain[c]
    return c == a

# independent verifier verdicts (ledgers/work/ver_out_K.tsv): a fold/split they reject or are uncertain about is NOT applied
ver = {}
for vp in sorted(glob.glob(os.path.join(W, "ver_out_*.tsv"))):
    for r in tsv(vp):
        ver[(r["type"].strip().upper(), key(r["key"]))] = (r["verdict"].strip().lower(), r.get("note", ""))
rej, folds, splits, meta, fov, gov = [], [], [], [], [], []
decisions = {}
for p in sorted(glob.glob(os.path.join(W, "dec_*.tsv"))):
    if p.endswith("dec_rejected.tsv"): continue
    for r in tsv(p):
        k = (r.get("key") or "").strip(); d = (r.get("decision") or "").strip().lower()
        tg, et, note = (r.get("target") or "").strip(), (r.get("etype") or "").strip(), (r.get("note") or "").strip()
        src = os.path.basename(p)
        if not k or not d: rej.append((src, "empty key/decision", k, d, tg)); continue
        if d in ("ok", "change_alias", "change_stop", "change_entity"):          # manual package, DECISION rows
            if d == "change_alias":
                if key(tg) not in ents: rej.append((src, "change_alias target missing", k, d, tg)); continue
                gov.append((k, "alias", tg, "", f"{TAG}: {note}"))
            elif d == "change_stop": gov.append((k, "stop", "", "", f"{TAG}: {note}"))
            elif d == "change_entity":
                if not tg or not et: rej.append((src, "change_entity needs target+etype", k, d, tg)); continue
                gov.append((k, "entity", tg, et, f"{TAG}: {note}"))
            continue
        kk = key(k)
        if kk not in ents: rej.append((src, "key not an entity", k, d, tg)); continue
        if kk in decisions: rej.append((src, "duplicate decision for key", k, d, tg)); continue
        decisions[kk] = d
        if d == "fold":
            t = key(tg)
            if t not in ents or t == kk: rej.append((src, "fold target missing or self", k, d, tg)); continue
            if kk in protected: rej.append((src, "key is a never-merge alias", k, d, tg)); continue
            if reaches(kk, t): rej.append((src, "fold would create a cycle", k, d, tg)); continue
            vv = ver.get(("FOLD", kk))
            if vv and vv[0] in ("reject", "uncertain"):
                rej.append((src, "verifier " + vv[0], k, d, tg)); meta.append((kk, et, "keep", "", "fold not applied (verifier " + vv[0] + "): " + vv[1])); continue
            chain[kk] = t; folds.append((kk, t, f"{TAG}: {note}"))
        elif d == "split":
            ts = [key(x) for x in tg.split("|") if x.strip()]
            if len(ts) < 2 or any(t not in ents for t in ts) or kk in ts: rej.append((src, "split targets invalid", k, d, tg)); continue
            vv = ver.get(("SPLIT", kk))
            if vv and vv[0] in ("reject", "uncertain"):
                rej.append((src, "verifier " + vv[0], k, d, tg)); meta.append((kk, et, "keep", "", "split not applied (verifier " + vv[0] + "): " + vv[1])); continue
            splits.append((kk, "|".join(ts), note))
        elif d in ("topic", "keep"):
            meta.append((kk, et or ("topic" if d == "topic" else ""), d, key(tg) if tg else "", note))
        elif d == "homonym":
            ok = True; rows = []
            for part in [x for x in tg.split(";") if x.strip()]:
                nk, _, ids = part.partition("=")
                for s in [i.strip() for i in ids.split(",") if i.strip()]:
                    if sid_key.get(s) != kk: ok = False; break
                    rows.append((s, key(nk), nk.strip().title()))
            if not ok or not rows: rej.append((src, "homonym sids not all facts of the key", k, d, tg[:80])); continue
            fov.extend(rows); meta.append((kk, et, "keep", "", f"homonym split: {note}"))
        else:
            rej.append((src, "unknown decision", k, d, tg))

write(ov_path, ["alias", "canonical", "note"], [(r["alias"], r["canonical"], r["note"]) for r in ov] + [(a, c, n) for a, c, n in folds])
write(os.path.join(LED, "entity_splits.tsv"), ["key", "targets", "note"], splits)
write(os.path.join(LED, "entity_meta.tsv"), ["key", "etype", "decision", "home", "note"], meta)
write(os.path.join(LED, "fact_entity_overrides.tsv"), ["sid", "key", "display"], fov)
write(os.path.join(LED, "gap_decision_overrides.tsv"), ["term", "kind", "target", "etype", "note"], gov)
write(os.path.join(W, "dec_rejected.tsv"), ["file", "reason", "key", "decision", "target"], rej)
c = collections.Counter(decisions.values())
print(f"decisions {len(decisions)} {dict(c)}; folds {len(folds)} splits {len(splits)} meta {len(meta)} homonym facts {len(fov)} gap overrides {len(gov)}; rejected {len(rej)}")
