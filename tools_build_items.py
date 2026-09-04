"""Generate the item files.

Answer positions are assigned deterministically rather than left wherever the
correct option happened to be written, so no letter is over-represented. A
suite whose answer key leans on one position rewards a model's formatting
habits instead of its Dutch.
"""
import json, random
from pathlib import Path

OUT = Path("items"); OUT.mkdir(exist_ok=True)
rng = random.Random(20260904)

def mcq(cat, n, prompt, correct, distractors, note="", difficulty="core"):
    return {"_cat": cat, "id": f"{cat}-{n:03d}", "type": "mcq", "prompt": prompt,
            "_correct": correct, "_distractors": distractors, "note": note, "difficulty": difficulty}

def write(cat, rows):
    out = []
    # Round-robin the gold position so every letter is used equally.
    for i, r in enumerate(rows):
        opts = list(r["_distractors"])
        pos = i % (len(opts) + 1)
        opts.insert(pos, r["_correct"])
        out.append({"id": r["id"], "category": cat, "type": "mcq", "prompt": r["prompt"],
                    "choices": opts, "answer": r["_correct"],
                    "note": r["note"], "difficulty": r["difficulty"]})
    p = OUT / f"{cat}.jsonl"
    p.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n", encoding="utf-8")
    print(f"{cat}: {len(out)} items -> {p}")

# ---------------------------------------------------------------- de / het
DEHET = [
    ("beleid","het"),("bestuur","het"),("personeel","het"),("salaris","het"),
    ("overleg","het"),("besluit","het"),("onderzoek","het"),("rapport","het"),
    ("verslag","het"),("aantal","het"),("percentage","het"),("vermogen","het"),
    ("vertrouwen","het"),("gedrag","het"),("geheugen","het"),("gevolg","het"),
    ("gebrek","het"),("begrip","het"),("gezag","het"),("gereedschap","het"),
    ("procedure","de"),("hoeveelheid","de"),("regeling","de"),("directie","de"),
    ("vergoeding","de"),("vergadering","de"),("beslissing","de"),("samenvatting","de"),
    ("waarheid","de"),("vrijheid","de"),("ontwikkeling","de"),("mogelijkheid","de"),
    ("toekomst","de"),("macht","de"),("keuze","de"),("ervaring","de"),
    ("verandering","de"),("mening","de"),("nota","de"),("kans","de"),
]
rows=[]
for i,(w,art) in enumerate(DEHET,1):
    other = "de" if art=="het" else "het"
    rows.append(mcq("de_het", i, f"Welk lidwoord hoort bij het zelfstandig naamwoord “{w}”?",
                    art, [other],
                    note="Woorden op -heid, -ing, -ij en -tie zijn de-woorden; veel ge-...-nomen zijn het-woorden."))
write("de_het", rows)

# ---------------------------------------------------------------- spelling
SPELL = [
    ("pannenkoek","pannekoek","Tussen-n omdat 'pan' alleen een meervoud op -en heeft."),
    ("bessensap","bessesap","Tussen-n: 'bes' heeft alleen het meervoud 'bessen'."),
    ("boekenkast","boekekast","Tussen-n: 'boek' heeft alleen 'boeken'."),
    ("kippenhok","kippehok","Tussen-n: 'kip' heeft alleen 'kippen'."),
    ("paardenstal","paardestal","Tussen-n: 'paard' heeft alleen 'paarden'."),
    ("kattenbak","kattebak","Tussen-n: 'kat' heeft alleen 'katten'."),
    ("spinnenweb","spinneweb","Tussen-n: 'spin' heeft alleen 'spinnen'."),
    ("sterrenhemel","sterrehemel","Tussen-n: 'ster' heeft alleen 'sterren'."),
    ("krentenbrood","krentebrood","Tussen-n: 'krent' heeft alleen 'krenten'."),
    ("rozenstruik","rozestruik","Tussen-n: 'roos' heeft alleen 'rozen'."),
    ("bananenschil","bananeschil","Tussen-n: 'banaan' heeft alleen 'bananen'."),
    ("appelmoes","appelenmoes","Geen tussen-n: 'appel' heeft ook het meervoud 'appels'."),
    ("groentesoep","groentensoep","Geen tussen-n: 'groente' heeft ook het meervoud 'groentes'."),
    ("perenboom","pereboom","Tussen-n: 'peer' heeft alleen 'peren'."),
    ("muizenval","muizeval","Tussen-n: 'muis' heeft alleen 'muizen'."),
]
rows=[mcq("spelling", i, f"Welke spelling is correct volgens de officiële spelling?", c, [w], note=n)
      for i,(c,w,n) in enumerate(SPELL,1)]

DT = [
    ("Hij wordt morgen verwacht.","Hij word morgen verwacht.","Stam + t bij 'hij'."),
    ("Ik word morgen verwacht.","Ik wordt morgen verwacht.","Bij 'ik' alleen de stam, zonder t."),
    ("Word jij daar blij van?","Wordt jij daar blij van?","Bij inversie met 'jij' vervalt de t."),
    ("Hij vindt het lastig.","Hij vind het lastig.","Stam 'vind' + t."),
    ("Wat gebeurt er nu?","Wat gebeurd er nu?","Tegenwoordige tijd: stam + t."),
    ("Ik heb hem gemaild.","Ik heb hem gemailed.","Nederlands voltooid deelwoord: ge- + stam + d."),
    ("De trein is aangekomen.","De trein is aankomen.","Voltooid deelwoord van het scheidbare 'aankomen'."),
    ("Zij heeft het bestand geüpload.","Zij heeft het bestand geupload.","Trema op de u na ge-."),
    ("Hij heeft snel geswitcht.","Hij heeft snel geswitchd.","'t kofschip: 'switch' eindigt op een stemloze klank, dus -t."),
    ("We hebben gisteren gefietst.","We hebben gisteren gefietsd.","'t kofschip: stam op -ts, dus -t."),
    ("Zij zijn vorig jaar verhuisd.","Zij zijn vorig jaar verhuist.","Stam op stemhebbende -z-klank, dus -d."),
    ("Ik heb de hele dag gewerkt.","Ik heb de hele dag gewerkd.","'t kofschip: -k, dus -t."),
]
rows += [mcq("spelling", 100+i, "Welke zin is correct gespeld?", c, [w], note=n)
         for i,(c,w,n) in enumerate(DT,1)]
write("spelling", rows)

# ---------------------------------------------------------------- diminutives
DIM = [
    ("boom","boompje",["boomje","boomtje","boomkje"],"Na -m met lange klinker: -pje."),
    ("bloem","bloempje",["bloemje","bloemtje","bloemetje"],"Na -m: -pje. ('bloemetje' bestaat, maar betekent een boeketje.)"),
    ("arm","armpje",["armje","armtje","armetje"],"Na -m voorafgegaan door een medeklinker: -pje."),
    ("film","filmpje",["filmje","filmtje","filmetje"],"Na -m: -pje."),
    ("koning","koninkje",["koningje","koningtje","koningetje"],"Na -ing: -kje."),
    ("woning","woninkje",["woningje","woningtje","woningetje"],"Na -ing: -kje."),
    ("man","mannetje",["manje","mantje","manpje"],"Korte klinker + n: verdubbeling + -etje."),
    ("pan","pannetje",["panje","pantje","panpje"],"Korte klinker + n: verdubbeling + -etje."),
    ("zon","zonnetje",["zonje","zontje","zonpje"],"Korte klinker + n: verdubbeling + -etje."),
    ("brug","bruggetje",["brugje","brugtje","brugpje"],"Korte klinker + g: verdubbeling + -etje."),
    ("bel","belletje",["belje","beltje","belpje"],"Korte klinker + l: verdubbeling + -etje."),
    ("ding","dingetje",["dingje","dingkje","dingtje"],"Na -ing na korte klinker: -etje."),
    ("auto","autootje",["autotje","autoje","autoetje"],"Open lettergreep op -o: klinker verdubbelen + -tje."),
    ("foto","fotootje",["fototje","fotoje","fotoetje"],"Open lettergreep op -o: klinker verdubbelen + -tje."),
    ("paraplu","parapluutje",["paraplutje","parapluje","parapluïtje"],"Op -u: klinker verdubbelen + -tje."),
    ("taxi","taxietje",["taxitje","taxiitje","taxije"],"Op -i: -etje met tussen-e geschreven als 'ie'."),
    ("huis","huisje",["huistje","huisetje","huispje"],"Gewoon -je na -s."),
    ("schaap","schaapje",["schaaptje","schaapetje","schaappje"],"Gewoon -je na -p."),
]
rows=[mcq("diminutives", i, f"Wat is het correcte verkleinwoord van “{w}”?", c, d, note=n)
      for i,(w,c,d,n) in enumerate(DIM,1)]
write("diminutives", rows)

# ---------------------------------------------------------------- idioms
IDIOMS = [
    ("de kat uit de boom kijken","eerst afwachten voordat je iets doet",
     ["meteen tot actie overgaan","iemand streng terechtwijzen","iets heel precies uitzoeken"]),
    ("de knoop doorhakken","een knoop van een beslissing nemen",
     ["een probleem uit de weg gaan","een afspraak afzeggen","iets in stukken verdelen"]),
    ("met de deur in huis vallen","direct ter zake komen",
     ["onaangekondigd op bezoek gaan","een fout maken bij binnenkomst","te laat komen"]),
    ("een appeltje voor de dorst","geld dat je achter de hand houdt",
     ["een kleine beloning achteraf","een excuus om weg te gaan","een lichte maaltijd"]),
    ("de dans ontspringen","net aan een vervelende situatie ontkomen",
     ["ergens niet aan mee willen doen","de leiding nemen","onopvallend vertrekken"]),
    ("boter bij de vis","direct betalen, zonder uitstel",
     ["een overdreven eis stellen","twee zaken door elkaar halen","een gunst vragen"]),
    ("de plank misslaan","er volledig naast zitten",
     ["een kans laten lopen","hard maar onhandig werken","een ander de schuld geven"]),
    ("uit de losse pols","zonder voorbereiding, geïmproviseerd",
     ["met veel moeite","precies volgens de regels","in het geheim"]),
    ("met een sisser aflopen","zonder ernstige gevolgen eindigen",
     ["uitlopen op een ruzie","langzaam verdwijnen","onverwacht duur uitvallen"]),
    ("de kool en de geit sparen","het beide partijen naar de zin proberen te maken",
     ["heel zuinig leven","een keuze eindeloos uitstellen","de zwakste partij beschermen"]),
    ("een storm in een glas water","veel drukte om niets",
     ["een ruzie die lang doorwerkt","een plotselinge tegenslag","een klein probleem dat groot wordt"]),
    ("de handdoek in de ring gooien","opgeven",
     ["een conflict beginnen","een ander om hulp vragen","zich terugtrekken uit beleefdheid"]),
    ("iets onder de knie hebben","iets goed beheersen",
     ["iets geheim houden","iets net op tijd afmaken","iets stevig vastpakken"]),
    ("de puntjes op de i zetten","de laatste details afwerken",
     ["heel streng zijn","iets nauwkeurig uitleggen","de fouten van een ander aanwijzen"]),
    ("in het water vallen","niet doorgaan",
     ["mislukken door slecht weer","in vergetelheid raken","onverwacht goedkoop worden"]),
    ("roet in het eten gooien","de plannen bederven",
     ["een vies gerecht opdienen","onaangekondigd meeëten","een geheim verklappen"]),
    ("met twee maten meten","ongelijk oordelen over vergelijkbare gevallen",
     ["twee keer hetzelfde controleren","heel precies afwegen","twijfelen tussen twee opties"]),
    ("van een mug een olifant maken","iets kleins veel te groot maken",
     ["een leugen steeds herhalen","onnodig veel geld uitgeven","langzaam maar zeker groeien"]),
    ("de spijker op de kop slaan","precies het juiste zeggen",
     ["hard doorwerken","iets definitief afsluiten","toevallig gelijk krijgen"]),
    ("zijn handen in onschuld wassen","de verantwoordelijkheid van zich af schuiven",
     ["ergens spijt van hebben","zich netjes gedragen","een ruzie bijleggen"]),
    ("het hoofd koel houden","kalm blijven",
     ["afstandelijk doen","nuchter rekenen","zich niet laten overtuigen"]),
    ("de kastanjes uit het vuur halen","het vervelende werk voor een ander opknappen",
     ["op het laatste moment ingrijpen","van andermans werk profiteren","een gevaarlijke gok nemen"]),
]
rows=[mcq("idioms", i, f"Wat betekent de uitdrukking “{u}”?", c, d) for i,(u,c,d) in enumerate(IDIOMS,1)]
write("idioms", rows)

# ---------------------------------------------------------------- false friends
FF = [
    ("eventueel","mogelijk, misschien",["uiteindelijk","onvermijdelijk","regelmatig"],
     "Vals vriendje van het Engelse 'eventually'."),
    ("actueel","van dit moment, recent",["werkelijk, feitelijk","toevallig","gebruikelijk"],
     "Vals vriendje van het Engelse 'actual'."),
    ("brutaal","onbeschaamd, vrijpostig",["wreed, gewelddadig","eerlijk en direct","zeer sterk"],
     "Vals vriendje van het Engelse 'brutal'."),
    ("een magazijn","een opslagruimte",["een tijdschrift","een winkelketen","een wapenkamer"],
     "Vals vriendje van het Engelse 'magazine'."),
    ("solliciteren","naar een baan meedingen",["klanten benaderen","om een gunst vragen","een aanvraag indienen bij de gemeente"],
     "Vals vriendje van het Engelse 'to solicit'."),
    ("raar","vreemd",["zeldzaam","half doorbakken","ruw"],
     "Vals vriendje van het Engelse 'rare'."),
    ("slim","handig, intelligent",["slank","glad","sluw in negatieve zin"],
     "Vals vriendje van het Engelse 'slim'."),
    ("streng","strikt",["sterk","hevig","strak gespannen"],
     "Vals vriendje van het Engelse 'strong'."),
    ("de wet","de regelgeving",["nattigheid","de weddenschap","het gewicht"],
     "Vals vriendje van het Engelse 'wet'."),
    ("een college","een hoorcollege aan de universiteit",["een collega","een middelbare school","een bestuursorgaan van studenten"],
     "Vals vriendje van het Engelse 'college'."),
    ("de agenda","het afsprakenboekje of de planning",["de politieke bedoeling","de vergaderzaal","het verslag"],
     "In het Nederlands vooral de kalender of planning."),
    ("een miljard","1.000.000.000",["1.000.000","1.000.000.000.000","100.000.000"],
     "Nederlands 'miljard' = Engels 'billion'; 'biljoen' = Engels 'trillion'."),
    ("een biljoen","1.000.000.000.000",["1.000.000.000","1.000.000","10.000.000.000"],
     "Let op het verschil met het Engelse 'billion'."),
    ("de fabriek","de productielocatie",["het verzinsel","de stof","het merk"],
     "Vals vriendje van het Engelse 'fabric'."),
    ("dringend","urgent",["opdringerig","druk","streng"],
     "Niet te verwarren met 'dwingend'."),
    ("de directeur","de leidinggevende van een organisatie",["de regisseur van een film","de richting","de adviseur"],
     "De filmregisseur heet in het Nederlands 'regisseur'."),
    ("gijzelen","iemand vasthouden als gijzelaar",["iemand plagen","iemand overhalen","iemand vermommen"],
     ""),
    ("de winkel","de zaak waar je iets koopt",["het karretje","de hoek","het magazijn"],
     ""),
]
rows=[mcq("false_friends", i, f"Wat betekent “{w}” in het Nederlands?", c, d, note=n)
      for i,(w,c,d,n) in enumerate(FF,1)]
write("false_friends", rows)

# ---------------------------------------------------------------- word order
WO = [
    ("Ik bel je morgen op.",["Ik opbel je morgen.","Ik bel op je morgen.","Ik je morgen opbel."],
     "Scheidbaar werkwoord: het partikel gaat naar het einde van de hoofdzin."),
    ("Neem je het pakket mee?",["Neem je mee het pakket?","Meeneem je het pakket?","Je neemt het pakket mee?"],
     "Scheidbaar 'meenemen', partikel achteraan; vraagzin met inversie."),
    ("De trein komt om zes uur aan.",["De trein aankomt om zes uur.","De trein komt aan om zes uur.","De trein om zes uur aankomt."],
     "Scheidbaar 'aankomen': partikel op de laatste plaats."),
    ("Ik ga naar bed omdat ik moe ben.",["Ik ga naar bed omdat ik ben moe.","Ik ga naar bed omdat ben ik moe.","Ik ga naar bed omdat moe ik ben."],
     "In een bijzin staat de persoonsvorm achteraan."),
    ("Hij zei dat hij morgen komt.",["Hij zei dat komt hij morgen.","Hij zei dat hij komt morgen.","Hij zei dat morgen hij komt."],
     "Bijzin met 'dat': werkwoord achteraan."),
    ("Gisteren ben ik naar Amsterdam gegaan.",["Gisteren ik ben naar Amsterdam gegaan.","Gisteren ben naar Amsterdam ik gegaan.","Gisteren ik naar Amsterdam gegaan ben."],
     "Hoofdzin: de persoonsvorm staat op de tweede plaats."),
    ("Ik probeer hem vanavond op te bellen.",["Ik probeer hem vanavond te opbellen.","Ik probeer hem vanavond opbellen te.","Ik probeer op te bellen hem vanavond."],
     "Bij scheidbare werkwoorden komt 'te' tussen partikel en werkwoord."),
    ("Zij heeft de vergadering afgezegd.",["Zij heeft de vergadering gezegdaf.","Zij heeft afgezegd de vergadering.","Zij afgezegd heeft de vergadering."],
     "Voltooid deelwoord van 'afzeggen': partikel + ge- + stam."),
    ("Weet je waar hij woont?",["Weet je waar woont hij?","Weet je waar hij woont niet?","Weet jij waar woont hij?"],
     "Indirecte vraag is een bijzin: werkwoord achteraan."),
    ("Morgen moet ik vroeg opstaan.",["Morgen ik moet vroeg opstaan.","Morgen moet vroeg ik opstaan.","Morgen ik vroeg opstaan moet."],
     "Inversie na een vooropgeplaatste bepaling."),
    ("Hij heeft het boek nog niet gelezen.",["Hij heeft nog niet het boek gelezen.","Hij heeft het boek gelezen nog niet.","Hij nog niet het boek gelezen heeft."],
     "Ontkenning voor het voltooid deelwoord, na het bepaalde object."),
    ("Ik weet niet of zij meegaat.",["Ik weet niet of gaat zij mee.","Ik weet niet of zij gaat mee.","Ik weet niet of meegaat zij."],
     "Bijzin met 'of': persoonsvorm achteraan, scheidbaar werkwoord blijft heel."),
]
rows=[mcq("word_order", i, "Welke zin heeft de correcte woordvolgorde?", c, d, note=n)
      for i,(c,d,n) in enumerate(WO,1)]
write("word_order", rows)

# ---------------------------------------------------------------- register
REG = [
    ("Kunt u mij laten weten wanneer het u schikt?",
     ["Kun u mij laten weten wanneer het u schikt?","Kunt u mij laten weten wanneer het je schikt?","Kun jij mij laten weten wanneer het u schikt?"],
     "Consequent u-vorm, met de juiste werkwoordsvorm 'kunt'."),
    ("Wilt u zo vriendelijk zijn uw gegevens te controleren?",
     ["Wil u zo vriendelijk zijn uw gegevens te controleren?","Wilt u zo vriendelijk zijn je gegevens te controleren?","Wil jij zo vriendelijk zijn uw gegevens te controleren?"],
     "Bij 'u' hoort het bezittelijk voornaamwoord 'uw'."),
    ("Hebt u uw wachtwoord al gewijzigd?",
     ["Heb u uw wachtwoord al gewijzigd?","Hebt u jouw wachtwoord al gewijzigd?","Heeft jij uw wachtwoord al gewijzigd?"],
     "'Hebt u' en 'heeft u' zijn beide correct; 'heb u' niet."),
    ("Geachte mevrouw De Vries, hierbij stuur ik u de gevraagde stukken.",
     ["Beste mevrouw De Vries, hierbij stuur ik u de gevraagde stukken. Groetjes,","Geachte mevrouw De Vries, hierbij stuur ik je de gevraagde stukken.","Hoi mevrouw De Vries, hierbij stuur ik u de gevraagde stukken."],
     "Formele aanhef en formele aanspreekvorm horen bij elkaar."),
    ("Zou u zo vriendelijk willen zijn het formulier te ondertekenen?",
     ["Zou jij zo vriendelijk willen zijn het formulier te ondertekenen, meneer?","Zou u zo vriendelijk willen zijn het formulier te ondertekenen, joh?","Zou u zo vriendelijk wilt zijn het formulier te ondertekenen?"],
     "Register consequent formeel houden."),
    ("Ik hoor graag van u wanneer u de stukken hebt ontvangen.",
     ["Ik hoor graag van u wanneer je de stukken hebt ontvangen.","Ik hoor graag van jou wanneer u de stukken hebt ontvangen.","Ik hoor graag van u wanneer u de stukken heb ontvangen."],
     "Binnen één zin niet wisselen tussen u en je."),
    ("Met vriendelijke groet, Jan de Boer",
     ["Met vriendelijke groeten en de hartelijke groetjes, Jan de Boer","Groetjes en met vriendelijke groet, Jan de Boer","Hoogachtend groetjes, Jan de Boer"],
     "Eén afsluiting, passend bij het register."),
    ("Kun je me even bellen als je tijd hebt?",
     ["Kun je me even bellen als u tijd hebt?","Kunt je me even bellen als je tijd hebt?","Kun u me even bellen als je tijd heeft?"],
     "Consequent informeel: je-vorm in de hele zin."),
    ("Uw aanvraag is in behandeling genomen.",
     ["Jouw aanvraag is in behandeling genomen, meneer Jansen.","U aanvraag is in behandeling genomen.","Uw aanvraag is in behandeling genomen geworden."],
     "'Uw' als bezittelijk voornaamwoord bij 'u'."),
    ("Zoals afgesproken stuur ik u hierbij de offerte toe.",
     ["Zoals afgesproken stuur ik u hierbij de offerte na.","Zoals afgesproken stuur ik u hierbij de offerte op je mail.","Zoals afgesproken ik stuur u hierbij de offerte toe."],
     "Correcte inversie en passend werkwoord."),
]
rows=[mcq("register", i, "Welke formulering is qua aanspreekvorm en register correct en consequent?", c, d, note=n)
      for i,(c,d,n) in enumerate(REG,1)]
write("register", rows)

# ---------------------------------------------------------------- formatting
FMT = [
    ("Hoe schrijf je het getal duizend tweehonderd vierendertig komma vijf zes in Nederlandse notatie?",
     "1.234,56",["1,234.56","1234.56","1 234.56"],"Punt als duizendtalscheiding, komma als decimaalteken."),
    ("Welke notatie van een geldbedrag is in Nederland gebruikelijk?",
     "€ 1.250,00",["$1,250.00","€1,250.00","EUR 1.250.00"],"Euroteken vooraan, punt voor duizendtallen, komma voor centen."),
    ("Welke datumnotatie is de gangbare Nederlandse volgorde?",
     "04-09-2026",["09-04-2026","2026-04-09","04/09/26 AM"],"Dag-maand-jaar."),
    ("Hoe schrijf je een Nederlandse postcode correct?",
     "1234 AB",["AB 1234","1234AB-NL","1234-AB"],"Vier cijfers, spatie, twee hoofdletters."),
    ("Welke schrijfwijze van een tijdstip is in het Nederlands gebruikelijk?",
     "14.30 uur",["2:30 PM","14:30 PM","half drie 's middags PM"],"24-uursnotatie met een punt, gevolgd door 'uur'."),
    ("Wat is de correcte afkorting van het rangtelwoord 'eerste'?",
     "1e",["1st","1ste keer verkort als 1th","1º"],"In het Nederlands 1e of 1ste."),
    ("Hoe luidt de landcode voor een Nederlands mobiel nummer in internationale notatie?",
     "+31 6 12345678",["+31 06 12345678","0031-06-12345678","+31 (0)06 12345678"],"Na +31 vervalt de nul van het netnummer."),
    ("Welke schrijfwijze van een groot getal is correct in lopende Nederlandse tekst?",
     "3,5 miljoen euro",["3.5 miljoen euro","3,5 millioen euro","3.5 miljoen €"],"Decimaalkomma en de spelling 'miljoen'."),
    ("Hoe schrijf je een percentage correct in het Nederlands?",
     "12,5%",["12.5%","12,5 pct.","%12,5"],"Decimaalkomma, procentteken direct achter het getal."),
    ("Welke schrijfwijze van een jaartalbereik is correct?",
     "2020-2026",["2020~2026","2020 tot 2026 toe","2020/2026 jr."],"Streepje tussen begin- en eindjaar."),
]
rows=[mcq("formatting", i, p, c, d, note=n) for i,(p,c,d,n) in enumerate(FMT,1)]
write("formatting", rows)

# ---------------------------------------------------------------- civics
CIV = [
    ("Hoeveel provincies telt Nederland?","twaalf",["elf","dertien","tien"],""),
    ("Wat is de hoofdstad van Nederland?","Amsterdam",["Den Haag","Rotterdam","Utrecht"],
     "Den Haag is de regeringszetel, niet de hoofdstad."),
    ("Waar zetelen de regering en het parlement van Nederland?","Den Haag",
     ["Amsterdam","Utrecht","Arnhem"],"De hoofdstad en de regeringszetel verschillen."),
    ("Hoeveel zetels telt de Tweede Kamer?","150",["75","100","225"],""),
    ("Hoeveel zetels telt de Eerste Kamer?","75",["150","100","50"],""),
    ("Waar staat de afkorting BSN voor?","burgerservicenummer",
     ["basisschoolnummer","bankstelnummer","burgerlijk statusnummer"],""),
    ("Welke provincie is de jongste van Nederland?","Flevoland",
     ["Zeeland","Drenthe","Utrecht"],"Flevoland werd in 1986 een provincie."),
    ("Wat is de hoofdstad van de provincie Friesland?","Leeuwarden",
     ["Groningen","Assen","Zwolle"],""),
    ("Wat is de hoofdstad van de provincie Noord-Brabant?","'s-Hertogenbosch",
     ["Eindhoven","Tilburg","Breda"],"Eindhoven is de grootste stad, niet de hoofdstad."),
    ("Wat is de hoofdstad van de provincie Limburg?","Maastricht",
     ["Venlo","Roermond","Heerlen"],""),
    ("Wat is de hoofdstad van de provincie Overijssel?","Zwolle",
     ["Enschede","Deventer","Almelo"],""),
    ("Wat is de hoofdstad van de provincie Gelderland?","Arnhem",
     ["Nijmegen","Apeldoorn","Ede"],""),
    ("Wat is de hoofdstad van de provincie Drenthe?","Assen",
     ["Emmen","Hoogeveen","Meppel"],""),
    ("Wat is de hoofdstad van de provincie Flevoland?","Lelystad",
     ["Almere","Emmeloord","Dronten"],"Almere is de grootste stad van Flevoland."),
    ("Op welke datum wordt Koningsdag gevierd?","27 april",
     ["30 april","5 mei","4 mei"],"30 april was Koninginnedag."),
    ("Op welke datum is de Nationale Dodenherdenking?","4 mei",
     ["5 mei","27 april","11 november"],""),
    ("Op welke datum wordt Bevrijdingsdag gevierd?","5 mei",
     ["4 mei","27 april","15 augustus"],""),
    ("Wanneer wordt pakjesavond traditioneel gevierd?","5 december",
     ["6 december","24 december","31 december"],""),
    ("Welke instantie int in Nederland de belastingen?","de Belastingdienst",
     ["het UWV","de SVB","het CBS"],""),
    ("Welke organisatie publiceert de officiële Nederlandse statistieken?","het CBS",
     ["het RIVM","het KNMI","het CPB"],"CBS staat voor Centraal Bureau voor de Statistiek."),
    ("Welk instituut geeft in Nederland de weerswaarschuwingen af?","het KNMI",
     ["het RIVM","het CBS","Rijkswaterstaat"],""),
    ("Hoe heet de Nederlandse uitvoering van de Europese privacyverordening?","de AVG",
     ["de WBP","de AWB","de Wob"],"AVG: Algemene verordening gegevensbescherming."),
    ("Waarmee logt een burger in bij de Nederlandse overheid?","DigiD",
     ["iDEAL","BSN-pas","MijnOverheidpas"],"iDEAL is een betaalmethode."),
    ("Is een basisverzekering voor zorg in Nederland verplicht voor volwassen ingezetenen?","ja, die is verplicht",
     ["nee, die is vrijwillig","alleen voor werkenden","alleen boven een bepaald inkomen"],""),
]
rows=[mcq("civics", i, p, c, d, note=n) for i,(p,c,d,n) in enumerate(CIV,1)]
write("civics", rows)

# ---------------------------------------------------------------- variants
VAR = [
    ("Welk woord is typisch Belgisch-Nederlands voor een mobiele telefoon?","gsm",
     ["mobieltje","zaktelefoon","handtoestel"],""),
    ("Wat betekent “schoon” in het Belgisch-Nederlands doorgaans?","mooi",
     ["proper","leeg","goedkoop"],"In Nederland betekent 'schoon' vooral 'niet vuil'."),
    ("Welk woord gebruikt men in België voor een studentenkamer?","kot",
     ["hok","stek","bude"],""),
    ("Wat betekent “goesting” in het Belgisch-Nederlands?","zin, trek",
     ["haast","geluk","koppigheid"],""),
    ("Welk woord is in Nederland gebruikelijk voor wat men in België een “droogkuis” noemt?","stomerij",
     ["wasserette","droogtrommel","wasserij"],""),
    ("Wat is in Nederland het gangbare woord voor het Belgische “beenhouwer”?","slager",
     ["bakker","kruidenier","poelier"],""),
    ("Welk woord gebruikt men in België voor wat in Nederland een 'tosti' heet?","een croque-monsieur",
     ["een broodje warm","een panini","een boterham-au-four"],""),
    ("Wat betekent “poetsen” in het Belgisch-Nederlands doorgaans?","schoonmaken",
     ["oppoetsen tot glans","tanden borstelen","opruimen"],""),
]
rows=[mcq("variants", i, p, c, d, note=n) for i,(p,c,d,n) in enumerate(VAR,1)]
write("variants", rows)
