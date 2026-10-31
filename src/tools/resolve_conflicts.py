"""Phase 2.2: apply the reviewed resolution of ledgers/alias_conflicts.tsv to ledgers/alias_overrides.tsv.
UNION groups: every member maps to the first (canonical) entry. HOMONYM aliases: shared titles/epithets that point at different
entities; they are marked never-merge (empty canonical). Judgement is recorded in the note column; it rests on the agents'
cited `=` lines in Chapter_Notes plus series knowledge, and should be spot-checked in Phase 4. Idempotent; run before extract_facts.py."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "..", "ledgers", "alias_overrides.tsv")
UNION = [
 ["bezale", "beza", "bezale of maweil"],
 ["ceria springwalker", "ceria", "springwalker"],
 ["eloise du havin", "eloise", "tea witch"],
 ["nsiia", "empress nsiia of tiqr", "empress of beasts"],
 ["fierre", "serafierre", "serafierre val lischelle-drakle"],
 ["flos", "flos reimarch", "flos of reim", "king of destruction"],
 ["gazi", "gazi pathseeker", "lady pathseeker", "gazi the omniscient"],
 ["himilt val lischelle-drakle", "himilt", "himilt drakle"],
 ["klbkch", "klbkchhezeim", "klbkch the slayer", "senior guardsman klbkch", "klbkch (klbkchhezeim)"],
 ["krshia", "krshia silverfang", "honored krshia"],
 ["bethal walchais", "lady bethal walchais", "lady bethal", "lady bethal walcha??s", "lady walcha??s", "bethal"],
 ["laken", "laken godart", "the unseen emperor", "unseen emperor"],
 ["geneva", "geneva scala", "last light of baleros"],
 ["magnolia reinhart", "magnolia", "lady reinhart", "deadly flower of the north", "flower of izril"],
 ["mavika", "crow witch", "witch of flocks"],
 ["nawalishifra tannousin", "nawalishifra", "nawal"],
 ["osthia blackwing", "osthia"],
 ["quarass", "quarass (new)", "quarass lives"],
 ["cara o'sullivan", "cara", "queen of pop", "singer of terandria"],
 ["ryoka griffin", "ryoka", "wind runner", "wind runner of reizmelt"],
 ["remi canada", "remi", "r??mi canada"],
 ["salamani", "salamani the haste mage"],
 ["saliss of lights", "saliss", "saliss oliwing"],
 ["sir kerrig louis", "kerrig louis", "kerrig", "sir kerrig"],
 ["thomast veniral", "thomast", "sir thomast"],
 ["revine zecrew", "revine", "siren of savere"],
 ["teriarch", "eldavin", "grand mage eldavin", "grand magus eldavin"],
 ["tremborag", "great chieftain of dwarfhalls rest"],
 ["ilvriss", "ilvriss gemscale", "wall lord ilvriss"],
 ["zel shivertail", "zel", "general of the line", "tidebreaker"],
 ["mrsha", "mrsha the white rider", "doom of the raskghar"],
 ["az'kerash", "peril chandler"],
]
HOMONYM = ["ansill", "ansill", "chieftain", "great chieftain", "great chieftain of the mountain", "grand chieftain", "doombringer",
           "gecko of liscor", "general sserys", "grimalkin", "montressa du valeross", "ser solstice", "goblin slayer", "rabbiteater",
           "sergeant", "small queen", "stitch-girl", "the goblin lord", "the necromancer", "war walker", "kerash",
           "belavierr", "mistress of strands", "spider", "spider of lives", "stitch witch", "temptress", "the eater of threads",
           "threadstealer", "witch of calamity", "witch of webs", "mage runner", "elenope", "mons", "captain shieldscale",
           "your majesty", "honored krshia ", "sserys", "spear of the drakes", "yellow splatters", "hive soldier \"yellow splatters\""]
cur = {}
if os.path.exists(P):
    for r in csv.DictReader(open(P, encoding="utf-8"), delimiter="\t"): cur[r["alias"]] = (r["canonical"], r["note"])
for g in UNION:
    for a in g[1:]: cur[a] = (g[0], "conflict union (2.2)")
    cur.pop(g[0], None)           # the canonical must not map elsewhere
for a in HOMONYM: cur[a.strip()] = ("", "conflict homonym/shared title: never merge (2.2)")
with open(P, "w", encoding="utf-8", newline="\n") as o:
    o.write("alias\tcanonical\tnote\n" + "".join(f"{a}\t{c}\t{n}\n" for a, (c, n) in sorted(cur.items())))
print(len(UNION), "union groups;", len(HOMONYM), "homonyms;", len(cur), "override rows")
