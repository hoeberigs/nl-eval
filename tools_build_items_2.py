"""Second item batch. Additive: new categories are written whole, existing
categories are extended so the answer-position rotation continues."""
import json
from pathlib import Path

OUT = Path("items")

def mcq(cat, n, prompt, correct, distractors, note="", difficulty="core"):
    return {"_cat": cat, "id": f"{cat}-{n:03d}", "prompt": prompt, "_correct": correct,
            "_distractors": distractors, "note": note, "difficulty": difficulty}

def _emit(cat, rows, start):
    out = []
    for i, r in enumerate(rows):
        opts = list(r["_distractors"])
        pos = (start + i) % (len(opts) + 1)
        opts.insert(pos, r["_correct"])
        out.append({"id": r["id"], "category": cat, "type": "mcq", "prompt": r["prompt"],
                    "choices": opts, "answer": r["_correct"], "note": r["note"], "difficulty": r["difficulty"]})
    return out

def write(cat, rows):
    p = OUT / f"{cat}.jsonl"
    out = _emit(cat, rows, 0)
    p.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n", encoding="utf-8")
    print(f"{cat}: {len(out)} items (new)")

def extend(cat, rows):
    p = OUT / f"{cat}.jsonl"
    existing = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = {e["id"] for e in existing}
    rows = [r for r in rows if r["id"] not in ids]
    out = _emit(cat, rows, len(existing))
    with p.open("a", encoding="utf-8") as fh:
        for o in out: fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"{cat}: +{len(out)} -> {len(existing)+len(out)}")

def extend_exact(cat, rows):
    p = OUT / f"{cat}.jsonl"
    existing = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = {e["id"] for e in existing}
    rows = [r for r in rows if r["id"] not in ids]
    with p.open("a", encoding="utf-8") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{cat}: +{len(rows)} -> {len(existing)+len(rows)}")

# ---------------------------------------------------------------- werkwoordspelling
WW = [
 ("Hij ___ het niet.", "vindt", ["vind"]),
 ("Ik ___ het niet.", "vind", ["vindt"]),
 ("___ jij dat ook?", "Vind", ["Vindt"]),
 ("Zij ___ van jazz.", "houdt", ["houd"]),
 ("Ik ___ van jazz.", "houd", ["houdt"]),
 ("Hij ___ altijd snel.", "antwoordt", ["antwoord"]),
 ("Ze heeft meteen ___.", "geantwoord", ["geantwoordt"]),
 ("Het vliegtuig ___ om acht uur.", "landt", ["land"]),
 ("Het vliegtuig is net ___.", "geland", ["gelandt"]),
 ("Het vliegtuig ___ gisteren op tijd.", "landde", ["landte"]),
 ("Wat ___ er?", "gebeurt", ["gebeurd"]),
 ("Wat is er ___?", "gebeurd", ["gebeurt"]),
 ("Dat ___ wel vaker.", "gebeurt", ["gebeurd"]),
 ("De arts ___ de wond.", "verbindt", ["verbind"]),
 ("Ik ___ het rapport meteen.", "verzend", ["verzendt"]),
 ("Zij ___ het rapport meteen.", "verzendt", ["verzend"]),
 ("Het pakket is gisteren ___.", "verzonden", ["verzondt"]),
 ("Hij ___ zich om.", "kleedt", ["kleed"]),
 ("Ze ___ haar kind goed.", "voedt", ["voed"]),
 ("De klok ___ twaalf uur.", "luidt", ["luid"]),
 ("Het huis ___ af.", "brandt", ["brand"]),
 ("Het huis is ___.", "afgebrand", ["afgebrandt"]),
 ("Hij ___ mij een baan aan.", "biedt", ["bied"]),
 ("Ik ___ je koffie aan.", "bied", ["biedt"]),
 ("Ze ___ met de auto.", "rijdt", ["rijd"]),
 ("Ik ___ morgen naar Groningen.", "rijd", ["rijdt"]),
 ("Hij ___ de fles.", "schudt", ["schud"]),
 ("Zij ___ het team.", "leidt", ["leid"]),
 ("Het team ___ door haar.", "wordt geleid", ["wordt geleidt"]),
 ("___ u zich nog even bij de balie?", "Meldt", ["Meld"]),
 ("Ik ___ me morgen ziek.", "meld", ["meldt"]),
 ("Zij ___ zich gisteren ziek.", "meldde", ["meldte"]),
 ("Hij ___ zich bevrijd.", "voelde", ["voelte"]),
 ("Het kind ___ zich aan het glas.", "verwondt", ["verwond"]),
 ("De gemeente ___ de weg.", "verbreedt", ["verbreed"]),
 ("De weg ___ vorig jaar ___.", "werd verbreed", ["werd verbreedt"]),
 ("Hij ___ zich aan niemand.", "bindt", ["bind"]),
 ("Ik ___ het je aan.", "raad", ["raadt"]),
 ("Zij ___ het me af.", "raadt", ["raad"]),
 ("De wond ___ hard.", "bloedt", ["bloed"]),
 ("Wat ___ je daarmee?", "bedoel", ["bedoelt", "bedoeld"]),
 ("Dat had ik niet ___.", "bedoeld", ["bedoelt", "bedoelld"]),
 ("Hij ___ het goed.", "bedoelt", ["bedoeld", "bedoellt"]),
 ("Het is ___!", "gelukt", ["gelukd", "geluktt"]),
 ("Ze is ___ op je komst.", "verheugd", ["verheugt", "verheugdt"]),
 ("Hij ___ zich op je komst.", "verheugt", ["verheugd", "verheugdt"]),
 ("___ je dat?", "Word", ["Wordt", "Wort"]),
 ("Hij ___ morgen dertig.", "wordt", ["word", "wordtt"]),
 ("Ik ___ er moe van.", "word", ["wordt", "wort"]),
 ("Ze is arts ___.", "geworden", ["gewordden", "gewordt"]),
]
rows = [mcq("werkwoordspelling", i, f"Welke vorm hoort in de zin?\n\n{s}", c, d,
            note="werkwoordspelling: stam, d/t, voltooid deelwoord") for i, (s, c, d) in enumerate(WW, 1)]
write("werkwoordspelling", rows)

# ---------------------------------------------------------------- taaladvies
TA = [
 ("Hij is groter ___ ik.", "dan", ["als"], "vergrotende trap: dan"),
 ("Zij is even oud ___ haar buurman.", "als", ["dan"], "even ... als"),
 ("Ik heb ___ gisteren gezien.", "hen", ["hun"], "lijdend voorwerp: hen"),
 ("Ik heb ___ een brief gestuurd.", "hun", ["hen"], "meewerkend voorwerp zonder voorzetsel: hun"),
 ("Ik heb aan ___ geschreven.", "hen", ["hun"], "na voorzetsel: hen"),
 ("___ hebben gelijk.", "Zij", ["Hun"], "onderwerp: zij"),
 ("Dat is ___ auto.", "hun", ["hen"], "bezittelijk: hun"),
 ("Het boek ___ ik lees, is spannend.", "dat", ["wat"], "betrekkelijk voornaamwoord bij het-woord: dat"),
 ("Alles ___ hij zegt, klopt.", "wat", ["dat"], "na alles, iets, niets: wat"),
 ("Het huis ___ te koop staat, is oud.", "dat", ["wat", "die"], "het-woord: dat"),
 ("De vrouw ___ daar loopt, is mijn buurvrouw.", "die", ["dat"], "de-woord: die"),
 ("Het meisje ___ ik ken, woont hier.", "dat", ["die"], "het meisje: dat"),
 ("___ kinderen zijn hier?", "Welke", ["Welk"], "de-woord/meervoud: welke"),
 ("___ boek lees je?", "Welk", ["Welke"], "het-woord enkelvoud: welk"),
 ("___ van de twee wil je?", "Welke", ["Welk"], "zelfstandig gebruikt: welke"),
 ("Ik ken ___ allebei.", "hen", ["hun"], "lijdend voorwerp: hen"),
 ("Hij vroeg ___ ik kwam.", "of", ["als"], "indirecte vraag: of"),
 ("Ik weet niet ___ hij komt.", "of", ["als"], "indirecte vraag: of"),
 ("___ ik tijd heb, kom ik.", "Als", ["Of"], "voorwaarde: als"),
 ("Dit is een ___ vraag.", "moeilijke", ["moeilijk"], "de-woord: buigings-e"),
 ("Een ___ huis.", "mooi", ["mooie"], "het-woord, onbepaald: geen -e"),
 ("Het ___ huis.", "mooie", ["mooi"], "het-woord, bepaald: -e"),
 ("De ___ lijst vindt u in de bijlage.", "bijgevoegde", ["bijgevoegd"], "bijvoeglijk gebruikt deelwoord: -e"),
 ("Dat is ___ boek.", "mijn", ["me"], "bezittelijk: mijn"),
 ("Geef het aan ___.", "mij", ["mijn"], "persoonlijk voornaamwoord: mij"),
 ("___ komen morgen.", "Zij", ["Hun"], "onderwerp: zij"),
 ("Ik heb ___ nog niet gesproken.", "haar", ["zij"], "lijdend voorwerp: haar"),
 ("Hij kent ___ niet.", "ons", ["onze"], "lijdend voorwerp: ons"),
 ("___ huis staat te koop.", "Ons", ["Onze"], "het-woord: ons"),
 ("___ auto is kapot.", "Onze", ["Ons"], "de-woord: onze"),
 ("___ zijn gekomen.", "Beiden", ["Beide"], "zelfstandig, personen: beiden"),
 ("___ boeken zijn nieuw.", "Beide", ["Beiden"], "bijvoeglijk: beide"),
 ("___ waren blij, anderen niet.", "Sommigen", ["Sommige"], "zelfstandig, personen: -n"),
 ("De ___ kinderen zijn buiten.", "andere", ["anderen"], "bijvoeglijk: andere"),
 ("De ___ zijn al weg.", "anderen", ["andere"], "zelfstandig, personen: anderen"),
 ("Dat is de man ___ auto gestolen is.", "wiens", ["wie zijn"], "bezitsvorm: wiens"),
 ("Dat is de vrouw ___ hond is weggelopen.", "wier", ["wiens"], "vrouwelijk: wier"),
 ("Ik ben er ___ in geïnteresseerd.", "niet", ["geen"], "ontkenning van werkwoordgroep: niet"),
 ("Ik heb ___ tijd.", "geen", ["niet"], "ontkenning van onbepaald zelfstandig naamwoord: geen"),
 ("Hij werkt ___ hard.", "heel", ["hele"], "bijwoord: heel"),
 ("Een ___ dag lang.", "hele", ["heel"], "bijvoeglijk: hele"),
 ("Ze zei ___ ze morgen komt.", "dat", ["als"], "voegwoord: dat"),
 ("___ je klaar bent, mag je gaan.", "Zodra", ["Zodat"], "tijd: zodra"),
 ("Ik wacht ___ de bus.", "op", ["naar"], "wachten op"),
 ("Ze luistert ___ muziek.", "naar", ["aan"], "luisteren naar"),
 ("Hij vraagt ___ hulp.", "om", ["voor"], "vragen om"),
 ("Ik ben trots ___ je.", "op", ["van"], "trots op"),
 ("Zij is bang ___ spinnen.", "voor", ["van"], "bang voor"),
 ("Hij lijkt ___ zijn broer.", "op", ["aan"], "lijken op"),
 ("Ik denk ___ jou.", "aan", ["op"], "denken aan"),
]
rows = [mcq("taaladvies", i, f"Welk woord hoort in de zin?\n\n{s}", c, d, note=n) for i, (s, c, d, n) in enumerate(TA, 1)]
write("taaladvies", rows)
