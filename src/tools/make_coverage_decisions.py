"""One-off recorder for the Gate 1 coverage decisions (ledgers/coverage_decisions.tsv).
kind: alias (term is a variant of target), entity (needs its own entity file in Phase 2; target = working name),
bracket (a [Class]/[Skill]/[Spell]/system term covered by ledgers/brackets.tsv), stop (not an entity; reason in note).
Cites are the census first_cite from coverage_gaps.tsv. Re-run after editing D."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "..", "ledgers")

A, E, B, S = "alias", "entity", "bracket", "stop"
D = {
 "Dragons": (A, "Dragon", "species plural"),
 "Griffins": (A, "Griffin", "species plural"),
 "Manticores": (A, "Manticore", "species plural"),
 "Manticore": (E, "Manticore", "species"),
 "Nagas": (A, "Naga", "species plural"),
 "Gorgons": (A, "Gorgon", "species plural"),
 "Gorgon": (E, "Gorgon", "species"),
 "The Gorgon": (A, "Gorgon", "a specific Gorgon in 7.34C; resolve identity in Phase 2"),
 "Gargoyle": (E, "Gargoyle", "species"),
 "Centauress": (E, "The Centauress", "epithet used in 6.05D onward; resolve identity in Phase 2"),
 "The Centauress": (A, "Centauress", "variant"),
 "Lizardman": (E, "Lizardman", "Geneva-thread term (1.01D); resolve identity/species in Phase 2"),
 "The Lizardman": (A, "Lizardman", "variant"),
 "Lizardwoman": (E, "Lizardwoman", "Geneva-thread term (1.00D); resolve in Phase 2"),
 "The Lizardwoman": (A, "Lizardwoman", "variant"),
 "The Squirrel-woman": (E, "Squirrel-woman", "unnamed figure in the Niers interlude; resolve in Phase 2"),
 "Bagrhavens": (E, "Bagrhaven", "people/creatures in Book 7 (5.05); resolve in Phase 2"),
 "Drowned Ships": (E, "Drowned Ship", "ship type, Book 16"),
 "Earther": (E, "Earthers", "people from Earth"),
 "God": (E, "God", "in-world belief/religion topic"),
 "Ancestors": (E, "Ancestors", "exclamation and ancestor veneration; resolve in Phase 2"),
 "Councilmembers": (E, "Council of Liscor", "generic address in 6.22D; fold into the Council entity"),
 "Klb": (A, "Klbkch", "Erin's half-remembered form in 1.12"),
 "Comrade Pisces": (A, "Pisces", "title used by Ceria"),
 "Rag’s": (A, "Rags", "possessive typo"),
 "Reinharts": (A, "Reinhart", "family plural"),
 "Bastion-General": (E, "Bastion-General", "rank (Rhir/Antinium-war ranks, 7.34C)"),
 "The Bastion-General": (A, "Bastion-General", "variant"),
 "Bastion-General Quiteil": (E, "Bastion-General Quiteil", "character, 7.34C"),
 "Bastion-General Zavarial": (E, "Bastion-General Zavarial", "character, 7.34C"),
 "Prime Minister": (E, "Prime Minister", "office, Belchan (6.12K)"),
 "Mercenary Captain": (B, "[Mercenary Captain]", "class title"),
 "First Mate": (B, "[First Mate]", "class title"),
 "Depth Captain": (E, "Depth Captain", "Drowned Ship rank (7.11)"),
 "Thug Boss": (B, "[Thug Boss]", "class title"),
 "Veteran Scout": (B, "[Veteran Scout]", "class title"),
 "Beast Trainer": (B, "[Beast Trainer]", "class title"),
 "Crafters": (E, "Crafters", "Archmage/Illivere craft faction group (7.48K)"),
 "Grandmasters": (S, "", "chess rank discussed by Erin (1.20)"),
 "Shield Maiden": (B, "[Shield Maiden]", "class title"),
 "Revivalist": (E, "Revivalists", "Wistram faction"),
 "Martial Artists": (B, "[Martial Artists]", "class title"),
 "Aberrations": (E, "Aberrations", "Antinium-war creatures, 1.25; resolve in Phase 2"),
 "Humble Actor": (B, "[Humble Actor]", "system/title entry in the Call interlude"),
 "Ice Spikes": (B, "[Ice Spikes]", "spell"),
 "Lightning Bolt": (B, "[Lightning Bolt]", "spell"),
 "Conditions Met": (S, "", "system-message phrase inside class-change prompts"),
 "Users Connected": (S, "", "interface text in Interlude_The_Call"),
 "Guilds": (A, "Adventurers' Guild", "plural; also Runner's and other guilds, resolve in Phase 2"),
 "Adventurer’s Guilds": (A, "Adventurers' Guild", "plural"),
 "Runner’s Guilds": (A, "Runner's Guild", "plural"),
 "Chandrarian": (A, "Chandrar", "demonym"),
 "Terandrians": (A, "Terandria", "demonym"),
 "Dwarven": (A, "Dwarf", "adjective"),
 "Ants": (S, "", "common noun for ordinary ants"),
 "English": (S, "", "Earth language reference"),
 "Japanese": (S, "", "Earth demonym/language reference"),
 "Asian": (S, "", "Earth demonym reference"),
 "The Asian": (S, "", "Earth demonym reference (unnamed Earther)"),
 "Australian": (S, "", "Earth demonym reference"),
 "The Australian": (S, "", "Earth demonym reference (unnamed Earther)"),
 "Australia": (S, "", "Earth place reference"),
 "German": (S, "", "Earth demonym reference"),
 "Japan": (S, "", "Earth place reference"),
 "The Swedish": (S, "", "Earth demonym reference"),
 "Othello": (S, "", "Earth play named in 4.11"),
}
gaps = {r["term"]: r for r in csv.DictReader(open(os.path.join(LED, "coverage_gaps.tsv"), encoding="utf-8"), delimiter="\t")}
missing = [t for t in gaps if t not in D]
extra = [t for t in D if t not in gaps]
with open(os.path.join(LED, "coverage_decisions.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("term\tkind\ttarget\tnote\tfirst_cite\n")
    for t, (k, tg, n) in D.items():
        o.write(f"{t}\t{k}\t{tg}\t{n}\t{gaps[t]['first_cite'] if t in gaps else ''}\n")
print("missing", missing, "extra", extra)
