"""Build seed packets for the Phase 3 foundation files (D-010).
Each packet = ledger facts (facts.jsonl) relevant to one area, ordered by seq, as TSV:
  id  seq  cite  entity  kind  text
Selection = entities of the listed etypes / name patterns  +  facts whose text matches a rules regex
(only kinds fact/belief/reveal, which are the explanatory ones). Packets are seeds only: agents must read the text.
Output: src/tools/cache/foundation/<area>.tsv (gitignored).  Run: python -I src/tools/make_foundation_work.py"""
import csv, json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "..", "ledgers")
OUT = os.path.join(HERE, "cache", "foundation")
os.makedirs(OUT, exist_ok=True)
ents = {r["key"]: r for r in csv.DictReader(open(os.path.join(LED, "entities.tsv"), encoding="utf-8-sig"), delimiter="\t")}
F = [json.loads(l) for l in open(os.path.join(LED, "facts.jsonl"), encoding="utf-8")]
I = re.I
AREAS = {
    "levels": dict(
        names=r"^(levelling|levels|classes|skills|class merging|innkeepers|\[healer\]|runners|\[cleric\]|fearless|the \[geomancer\]|goblin \[cooks\]|adventurer ranks|silver-rank|bronze-rank adventurers|named-rank adventurers|gold-rank (teams|adventurers))$",
        text=r"\blevel(ing|ling|s)?\b.*\b(cap|up|rule|how|class|skill)|\bclass(es)?\b.*(change|merg|evolv|consolid|choose|rare|unique|require)|\bskills?\b.*(evolv|learn|gain|requir|can be|are |is a)|\[status\]|\bstatus\b|\bcondition\b|\btitles?\b.*\b(gain|grant|earn)|\bnames? (are|is)\b|\bcap\b|\bprestige|level 30|level 20|class obtained|\bnew class|\bhighest[- ]level"),
    "magic": dict(
        names=r"^(magic|tier magic|spellbooks|alchemy|healing potions|preservation runes|magic door|door|pallass door|petals of death|ritual|wistram.*|wistram students|wistram team|messenger seals|bag of holding|compartments of holding|teleport network|errant traveller|silent box)$",
        text=r"\bmana\b|\bspells?\b|\btier\b|\bmagic(al)?\b.*(is|are|can|cannot|requires?)|\benchant|\brunes?\b|\balchem|\bpotion|\bscroll|\bartifact|\bteleport|\bscrying|\bgolem|\bnecromanc|\bwand\b|\bstaff\b|\bcurse|\bhex\b|\baura\b|\britual"),
    "cosmology": dict(
        names=r"^(dungeon|magical dungeon|gods|sea's bargain|aberration|four walls|santa claus|the world|dead|funeral|hoard|treasure|loot)$",
        text=r"\bgods?\b|\bdeit(y|ies)\b|\bspirit(s)?\b|\bshrine|\bworship|\bpray|\bdungeons?\b|\bafterlife|\bghost|\bundead|\bsoul|\bplanes?\b|\bearth\b.*(world|summon|portal)|\bsummon(ed)?\b|\bname\b.*(of|is a)|\bthe fae\b|\bfaerie|\bfae\b|\bsea\b.*\bbargain|\bomen|\bdeath\b|\bhell\b|\bprophe|\bseer|\bcosmic|\bdragon\b.*(ancient|old)"),
    "species": dict(
        etypes={"species", "concept"},
        names=r"^(drakes?|gnolls?|humans?|antinium.*|goblins?.*|half-elves|elves|elf|dwarves|selphids?|dullahans?|vampires|fae|frost faeries|centaurs?|minotaurs?|garuda|lizardfolk|beastkin|djinni|naga|ogres|harpies|gazers|giants?|golems?|raskghar|stitch-people|string people|fraerlings|scalelings|war walkers|earthers|true antinium|demons|witches|centenium|infested|drowned (man|folk)|fair folk|fairies)$",
        text=r"\bspecies\b|\brace\b|\bracial\b|\bsubspecies\b|\bhalf-|\blifespan\b|\bhive\b|\bqueen\b.*antinium|\bantinium\b.*\b(born|grow|eat|breed)|\bgnolls?\b.*(tribe|cub|scent|fur)|\bdrakes?\b.*(scale|wing|egg|city)|\bgoblins?\b.*(tribe|chieftain|king|lord|born)|\bdwarf|\belf\b|\belves"),
    "creatures": dict(etypes={"creature"}, names=r"^$",
        text=r"\bmonsters?\b|\bbeast(s)?\b|\bdragon|\bwyvern|\bmothbear|\bcorusdeer|\bgriffin|\bshield spider|\bsilverfang|\bwolf|\bgolem\b|\bslime|\bcrelers?|\bgrimalkin|\bundead\b|\bwraith|\bzombie|\bskeleton|\bghoul"),
    "primer": dict(names=r"^(the world|earthers|summoned humans|narrator|the wandering inn)$",
        text=r"\bcontinent|\bizril\b.*(is|has|lies)|\bbaleros\b.*(is|has|lies)|\bterandria\b.*(is|has|lies)|\bchandrar\b.*(is|has|lies)|\bnorth(ern)? (continent|kingdom)|\bkingdom\b.*\b(is|has|rules)|\bempire\b.*(is|has)|\bmap\b|\bcalendar|\bseason|\bholiday|\bwinter\b.*(solstice|long|season)|\bsolstice\b|\bmonths?\b|\bdays? of the week"),
}
by_ent = collections.defaultdict(list)
for f in F: by_ent[f["key"]].append(f)
for area, c in AREAS.items():
    nm = re.compile(c.get("names", "^$"), I); tx = re.compile(c["text"], I); et = c.get("etypes", set())
    pick = {}
    for key, r in ents.items():
        if nm.search(r["display"]) or nm.search(key) or r["etype"] in et:
            for f in by_ent[key]: pick[f["id"]] = f
    seeds = len(pick)
    for f in F:
        if f["id"] in pick: continue
        r = ents.get(f["key"], {})
        if f["kind"] not in ("fact", "belief", "reveal"): continue
        if tx.search(f["text"]): pick[f["id"]] = f
    rows = sorted(pick.values(), key=lambda f: (f["seq"], f["id"]))
    with open(os.path.join(OUT, area + ".tsv"), "w", encoding="utf-8", newline="") as fh:
        fh.write("id\tseq\tcite\tentity\tkind\ttext\n")
        for f in rows:
            fh.write("\t".join([f["id"], str(f["seq"]), f["cite"], f["entity"], f["kind"], f["text"].replace("\t", " ").replace("\n", " ")]) + "\n")
    print(f"{area:10s} entity-facts {seeds:5d} total {len(rows):5d}")
