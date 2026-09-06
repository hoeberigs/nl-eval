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

# ============ expansion (2026-09) ============================================
# Thin categories first: variants, register, formatting and word_order carried
# only 8-12 items each, too few for a per-category score to mean anything.

def extend(cat, rows):
    """Append to an existing category, continuing the answer-position rotation."""
    path = OUT / f"{cat}.jsonl"
    existing = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    start = len(existing)
    out = []
    for i, r in enumerate(rows):
        opts = list(r["_distractors"])
        pos = (start + i) % (len(opts) + 1)
        opts.insert(pos, r["_correct"])
        out.append({"id": r["id"], "category": cat, "type": "mcq", "prompt": r["prompt"],
                    "choices": opts, "answer": r["_correct"],
                    "note": r["note"], "difficulty": r["difficulty"]})
    path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in existing + out) + "\n",
                    encoding="utf-8")
    print(f"{cat}: {len(existing)} + {len(out)} = {len(existing)+len(out)} items")


DEHET2 = [
 ("verzoek","het"),("overzicht","het"),("voorstel","het"),("contract","het"),
 ("project","het"),("systeem","het"),("netwerk","het"),("model","het"),
 ("doel","het"),("budget","het"),("resultaat","het"),("proces","het"),
 ("niveau","het"),("bedrag","het"),("tarief","het"),("formulier","het"),
 ("dossier","het"),("kenmerk","het"),("criterium","het"),("uitgangspunt","het"),
 ("aanvraag","de"),("afspraak","de"),("opdracht","de"),("planning","de"),
 ("begroting","de"),("uitkomst","de"),("methode","de"),("aanpak","de"),
 ("verwachting","de"),("doelstelling","de"),("samenwerking","de"),("bijdrage","de"),
 ("toegang","de"),("termijn","de"),("voorwaarde","de"),("bevoegdheid","de"),
 ("verplichting","de"),("vergunning","de"),("invulling","de"),("wijziging","de"),
]
extend("de_het",[mcq("de_het",100+i,f"Welk lidwoord hoort bij het zelfstandig naamwoord \u201c{w}\u201d?",
        a,["de" if a=="het" else "het"],
        note="Woorden op -ing, -heid en -tie zijn de-woorden.") for i,(w,a) in enumerate(DEHET2,1)])

SPELL2 = [
 ("hondenhok","hondehok","Tussen-n: 'hond' heeft alleen 'honden'."),
 ("schapenwol","schapewol","Tussen-n: 'schaap' heeft alleen 'schapen'."),
 ("geitenkaas","geitekaas","Tussen-n: 'geit' heeft alleen 'geiten'."),
 ("koeienmelk","koeiemelk","Tussen-n: 'koe' heeft alleen 'koeien'."),
 ("vliegenmepper","vliegemepper","Tussen-n: 'vlieg' heeft alleen 'vliegen'."),
 ("mierenhoop","mierehoop","Tussen-n: 'mier' heeft alleen 'mieren'."),
 ("bijenkorf","bijekorf","Tussen-n: 'bij' heeft alleen 'bijen'."),
 ("aardbeienjam","aardbeiejam","Tussen-n: 'aardbei' heeft alleen 'aardbeien'."),
 ("notenkraker","nootkraker","Tussen-n: 'noot' heeft alleen 'noten'."),
 ("tandenborstel","tandeborstel","Tussen-n: 'tand' heeft alleen 'tanden'."),
 ("wortelsap","wortelensap","Geen tussen-n: 'wortel' heeft ook het meervoud 'wortels'."),
]
DT2 = [
 ("Hij antwoordt meteen.","Hij antwoord meteen.","Stam 'antwoord' + t bij 'hij'."),
 ("Antwoord jij even?","Antwoordt jij even?","Bij inversie met 'jij' vervalt de t."),
 ("Zij bereidt de vergadering voor.","Zij bereid de vergadering voor.","Stam + t bij 'zij' enkelvoud."),
 ("Het bestand is verspreid onder de deelnemers.","Het bestand is verspreidt onder de deelnemers.","Voltooid deelwoord op -d."),
 ("We hebben de planning gecheckt.","We hebben de planning gechecked.","'t kofschip: stam op -ck, dus -t."),
 ("De offerte is vorige week gepland.","De offerte is vorige week geplant.","'gepland' hoort bij plannen, 'geplant' bij planten."),
 ("Zij heeft het systeem ge\u00fcpdatet.","Zij heeft het systeem geupdated.","Trema op de u, en 't kofschip geeft -t."),
]
extend("spelling",
  [mcq("spelling",200+i,"Welke spelling is correct volgens de offici\u00eble spelling?",c,[w],note=n)
   for i,(c,w,n) in enumerate(SPELL2,1)] +
  [mcq("spelling",300+i,"Welke zin is correct gespeld?",c,[w],note=n)
   for i,(c,w,n) in enumerate(DT2,1)])

WO2 = [
 ("Ik weet dat hij het boek heeft gelezen.",["Ik weet dat hij heeft het boek gelezen.","Ik weet dat heeft hij het boek gelezen.","Ik weet dat hij het boek gelezen heeft niet."],"Bijzin: werkwoordelijke eindgroep achteraan."),
 ("Wanneer komt de trein aan?",["Wanneer de trein aankomt?","Wanneer aankomt de trein?","Wanneer komt aan de trein?"],"Vraagzin met inversie; scheidbaar partikel achteraan."),
 ("Hij vroeg of ik meeging.",["Hij vroeg of ging ik mee.","Hij vroeg of ik ging mee.","Hij vroeg of meeging ik."],"Bijzin met 'of': persoonsvorm achteraan."),
 ("Omdat het regende, bleven we thuis.",["Omdat het regende, we bleven thuis.","Omdat regende het, bleven we thuis.","Omdat het regende, thuis bleven we."],"Na een vooropgeplaatste bijzin volgt inversie."),
 ("Ik ben van plan om volgende week te beginnen.",["Ik ben van plan om volgende week beginnen te.","Ik ben van plan volgende week om te beginnen.","Ik ben van plan om te volgende week beginnen."],"'om ... te' omsluit de infinitief."),
 ("Nooit heb ik zoiets gezien.",["Nooit ik heb zoiets gezien.","Nooit heb zoiets ik gezien.","Nooit ik zoiets gezien heb."],"Na vooropplaatsing van 'nooit' volgt inversie."),
 ("Zij zei dat ze het rapport morgen zou afronden.",["Zij zei dat ze zou het rapport morgen afronden.","Zij zei dat zou ze het rapport morgen afronden.","Zij zei dat ze het rapport morgen afronden zou niet."],"Bijzin: hulpwerkwoord in de eindgroep."),
 ("Het rapport dat ik gisteren heb gelezen, was uitstekend.",["Het rapport dat ik heb gisteren gelezen, was uitstekend.","Het rapport dat heb ik gisteren gelezen, was uitstekend.","Het rapport dat ik gisteren gelezen heb was uitstekend niet."],"Betrekkelijke bijzin met eindgroep."),
 ("Morgen ga ik de offerte versturen.",["Morgen ik ga de offerte versturen.","Morgen ga de offerte ik versturen.","Morgen ik de offerte versturen ga."],"Inversie na een vooropgeplaatste bepaling."),
 ("Hij heeft de vergadering moeten afzeggen.",["Hij heeft de vergadering afzeggen moeten niet.","Hij heeft moeten de vergadering afzeggen.","Hij heeft de vergadering afgezegd moeten."],"Vervangende infinitief in de eindgroep."),
]
extend("word_order",[mcq("word_order",200+i,"Welke zin heeft de correcte woordvolgorde?",c,d,note=n)
        for i,(c,d,n) in enumerate(WO2,1)])

REG2 = [
 ("Ik verzoek u vriendelijk het formulier ondertekend te retourneren.",
  ["Ik verzoek jou vriendelijk het formulier ondertekend te retourneren, meneer.",
   "Ik verzoek u vriendelijk het formulier ondertekend te retourneren, joh.",
   "Ik verzoekt u vriendelijk het formulier ondertekend te retourneren."],
  "Formeel verzoek, consequent in de u-vorm."),
 ("Mocht u nog vragen hebben, dan hoor ik het graag.",
  ["Mocht je nog vragen hebben, dan hoor ik het graag, geachte heer.",
   "Mocht u nog vragen hebben, dan hoor ik het graag van jou.",
   "Mocht u nog vragen hebt, dan hoor ik het graag."],
  "Binnen één zin niet wisselen tussen u en je."),
 ("Bij voorbaat dank voor uw medewerking.",
  ["Bij voorbaat dank voor jouw medewerking, geachte mevrouw.",
   "Bij voorbaat bedankt voor uw medewerking, thanks.",
   "Bij voorbaat dank voor u medewerking."],
  "'uw' is het bezittelijk voornaamwoord bij 'u'."),
 ("Wij zien uw reactie graag tegemoet.",
  ["Wij zien jouw reactie graag tegemoet, geachte heer.",
   "Wij zien uw reactie graag tegemoed.",
   "Wij ziet uw reactie graag tegemoet."],
  "Vaste formele afsluitzin."),
 ("Hierbij bevestig ik onze afspraak van dinsdag 8 september.",
  ["Hierbij bevestig ik onze afspraak van dinsdag 8 september, doei.",
   "Hierbij ik bevestig onze afspraak van dinsdag 8 september.",
   "Hierbij bevestigd ik onze afspraak van dinsdag 8 september."],
  "Inversie na 'hierbij', en bevestig zonder d."),
 ("Kun je me even laten weten of het je lukt?",
  ["Kun je me even laten weten of het u lukt?",
   "Kunt je me even laten weten of het je lukt?",
   "Kun u me even laten weten of het je lukt?"],
  "Consequent informeel: je-vorm in de hele zin."),
 ("Zou u zo vriendelijk willen zijn het contract te ondertekenen?",
  ["Zou u zo vriendelijk wilt zijn het contract te ondertekenen?",
   "Zou jij zo vriendelijk willen zijn het contract te ondertekenen, geachte heer?",
   "Zou u zo vriendelijk willen zijn het contract te tekenen, joh?"],
  "Beleefde vraagvorm met correcte werkwoordsvorm."),
 ("Geachte heer De Vries, naar aanleiding van ons gesprek stuur ik u de stukken toe.",
  ["Hoi meneer De Vries, naar aanleiding van ons gesprek stuur ik u de stukken toe.",
   "Geachte heer De Vries, naar aanleiding van ons gesprek stuur ik je de stukken toe.",
   "Geachte heer De Vries, naar aanleiding van ons gesprek ik stuur u de stukken toe."],
  "Aanhef en aanspreekvorm horen bij elkaar."),
 ("Met vriendelijke groet, Linda Hoeberigs",
  ["Met vriendelijke groetjes en hoogachtend, Linda Hoeberigs",
   "Hoogachtend groetjes, Linda Hoeberigs",
   "Met vriendelijke groet en de mazzel, Linda Hoeberigs"],
  "Eén afsluiting, passend bij het register."),
 ("Uw aanvraag is in behandeling genomen.",
  ["Jouw aanvraag is in behandeling genomen, geachte mevrouw.",
   "U aanvraag is in behandeling genomen.",
   "Uw aanvraag is in behandeling genomen geworden."],
  "Correcte lijdende vorm zonder 'geworden'."),
]
extend("register",[mcq("register",200+i,"Welke formulering is qua aanspreekvorm en register correct en consequent?",c,d,note=n)
        for i,(c,d,n) in enumerate(REG2,1)])

FMT2 = [
 ("Uit hoeveel cijfers bestaat een Nederlands burgerservicenummer (BSN)?","negen",["acht","tien","zeven"],""),
 ("Welke notatie van een Nederlands IBAN is correct?","NL91ABNA0417164300",
  ["NL91-ABNA-0417-1643-00","91NLABNA0417164300","NL91 ABNA 0417 1643 0000 00"],"Achttien tekens, zonder streepjes."),
 ("Hoe schrijf je een openingstijd-bereik in het Nederlands?","09.00–17.00 uur",
  ["9:00 AM – 5:00 PM","09,00–17,00 uur","09.00 tot 17.00 o'clock"],"24-uursnotatie met punt."),
 ("Welke schrijfwijze van een bedrag zonder centen is gangbaar?","€ 45,-",
  ["€ 45.00,-","45 € ,-","€ 45,00,-"],"Komma-streepje voor ronde bedragen."),
 ("Hoe verwijs je in het Nederlands naar een kalenderweek?","week 36",
  ["wk. 36e","36e week van het jaar 2026 n.C.","weeknummer #36"],""),
 ("Welke aanduiding van een kwartaal is in Nederlandse zakelijke tekst gangbaar?","het derde kwartaal",
  ["de derde kwartaal","kwartaal drie-en-twintig","Q-3e kwartaal"],"'Kwartaal' is een het-woord."),
 ("Hoe schrijf je een temperatuur correct in het Nederlands?","21,5 °C",
  ["21.5 °C","21,5°c","°C 21,5"],"Decimaalkomma en een spatie voor de eenheid."),
 ("Welke schrijfwijze van een telefoonnummer met netnummer is gangbaar?","020 123 45 67",
  ["+020-1234567","(020)1234567","020.123.4567"],""),
 ("Hoe schrijf je een datum met dag van de week correct?","dinsdag 8 september 2026",
  ["Dinsdag, 8 September 2026","dinsdag 8-9-2026 jaar","8 september 2026, dinsdag"],"Kleine letter voor dag en maand."),
 ("Welke afkorting hoort bij 'bijvoorbeeld'?","bijv.",["b.v.b.","bv.b","bijvb."],"'bv.' is Belgisch-Nederlands."),
]
extend("formatting",[mcq("formatting",200+i,p,c,d,note=n) for i,(p,c,d,n) in enumerate(FMT2,1)])

VAR2 = [
 ("Welk woord gebruikt men in België voor een vrachtwagen?","camion",["truck","laadwagen","vervoerder"],""),
 ("Welk woord gebruikt men in België voor een fiets?","velo",["rijwiel","trapper","stalen ros"],""),
 ("Wat betekent “kuisen” in het Belgisch-Nederlands?","schoonmaken",["kiezen","snoeien","zuiveren van fouten"],""),
 ("Wat betekent “ambetant” in het Belgisch-Nederlands?","vervelend",["ambitieus","onhandig","ongeduldig"],""),
 ("Welk woord gebruikt men in België voor een koelkast?","frigo",["koelbak","vrieskist","ijskast"],""),
 ("Welk woord gebruikt men in België voor jam?","confituur",["marmelade","siroop","gelei"],""),
 ("Welk woord gebruikt men in België voor een paraplu?","regenscherm",["regenkap","druppelscherm","regenhoed"],""),
 ("Welk woord gebruikt men in België voor een kantoor?","bureel",["burelen","kantoorzaal","werkkamer"],""),
 ("Hoe heet de bestuurder van een Belgische gemeente die in Nederland 'wethouder' heet?","schepen",
  ["gedeputeerde","raadsheer","gemeentesecretaris"],""),
 ("Welk woord gebruikt men in België voor een zitbank?","zetel",["divan","canapé","rustbank"],""),
 ("Wat betekent “goesting hebben” in het Belgisch-Nederlands?","zin hebben",["haast hebben","gelijk hebben","honger lijden"],""),
 ("Welk woord gebruikt men in Nederland voor het Belgische “droogkuis”?","stomerij",
  ["wasserette","droogkamer","reinigingsdienst"],""),
]
extend("variants",[mcq("variants",200+i,p,c,d,note=n) for i,(p,c,d,n) in enumerate(VAR2,1)])

FF2 = [
 ("globaal","in grote lijnen, ruwweg",["wereldwijd","volledig","gedetailleerd"],"Vals vriendje van het Engelse 'global'."),
 ("sympathiek","aardig, innemend",["meelevend","meegaand","zielig"],"Vals vriendje van het Engelse 'sympathetic'."),
 ("braaf","gehoorzaam, netjes",["dapper","eerlijk","sterk"],"Vals vriendje van het Engelse 'brave'."),
 ("een smoking","een avondkostuum",["het roken","een rookruimte","een rookverbod"],"Pseudo-anglicisme."),
 ("een beamer","een projector",["een laserpen","een schijnwerper","een afstandsbediening"],"Pseudo-anglicisme."),
 ("een oldtimer","een klassieke auto",["een oudere werknemer","een antieke klok","een veteraan"],"Pseudo-anglicisme."),
 ("pregnant","kernachtig, treffend",["zwanger","dringend","overdreven"],"Vals vriendje van het Engelse 'pregnant'."),
 ("de lectuur","het leesmateriaal",["de lezing","de voordracht","het college"],"Vals vriendje van het Engelse 'lecture'."),
]
extend("false_friends",[mcq("false_friends",200+i,f"Wat betekent “{w}” in het Nederlands?",c,d,note=n)
        for i,(w,c,d,n) in enumerate(FF2,1)])

IDI2 = [
 ("de touwtjes in handen hebben","de leiding hebben",["ergens aan vastzitten","een keuze uitstellen","iemand aan het lijntje houden"]),
 ("het roer omgooien","radicaal van koers veranderen",["de leiding overdragen","een besluit terugdraaien","hard ingrijpen"]),
 ("een blok aan het been","een blijvende belemmering",["een zware straf","een sterke steun","een vaste gewoonte"]),
 ("de kogel is door de kerk","de beslissing is genomen",["het gevaar is geweken","het geheim is uit","de ruzie is beslecht"]),
 ("met de gebakken peren zitten","met de nadelige gevolgen achterblijven",["onverwacht geluk hebben","in verlegenheid gebracht zijn","te veel hooi op de vork nemen"]),
 ("de hand in eigen boezem steken","de eigen rol kritisch bekijken",["een ander de schuld geven","iets toegeven onder druk","een geheim bewaren"]),
 ("van de hak op de tak springen","van het ene onderwerp naar het andere springen",["snel van mening veranderen","ongeduldig worden","onhandig te werk gaan"]),
 ("de dienst uitmaken","bepalen wat er gebeurt",["het werk verdelen","de gastheer zijn","de regels uitleggen"]),
 ("iets in de wacht slepen","iets binnenhalen",["iets uitstellen","iets verbergen","iets afdwingen"]),
 ("iemand een oor aannaaien","iemand bedriegen",["iemand streng toespreken","iemand overtuigen","iemand napraten"]),
]
extend("idioms",[mcq("idioms",200+i,f"Wat betekent de uitdrukking “{u}”?",c,d) for i,(u,c,d) in enumerate(IDI2,1)])

# ============ Schrijven: error correction, exact match ========================
# Writing scored without a judge. Each sentence carries exactly one error and
# exactly one correction, so the corrected sentence is a deterministic target.

def exact(cat, n, prompt, answer, note=""):
    return {"id": f"{cat}-{n:03d}", "category": cat, "type": "exact",
            "prompt": prompt, "answer": answer, "note": note, "difficulty": "core"}

def write_exact(cat, rows):
    p = OUT / f"{cat}.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(f"{cat}: {len(rows)} items -> {p}")

CORR = [
 ("Hij word morgen dertig.","Hij wordt morgen dertig.","d/t"),
 ("Ik wordt er gek van.","Ik word er gek van.","d/t"),
 ("Hij vind het niet leuk.","Hij vindt het niet leuk.","d/t"),
 ("Wat gebeurd er?","Wat gebeurt er?","d/t"),
 ("Het is gebeurt.","Het is gebeurd.","voltooid deelwoord"),
 ("Ik heb de brief gisteren verstuurt.","Ik heb de brief gisteren verstuurd.","voltooid deelwoord"),
 ("Ze hebben de vergadering afgezegt.","Ze hebben de vergadering afgezegd.","voltooid deelwoord"),
 ("Hij heeft gezegt dat hij komt.","Hij heeft gezegd dat hij komt.","voltooid deelwoord"),
 ("Antwoordt jij op mijn mail?","Antwoord jij op mijn mail?","inversie"),
 ("Hij wilt niet.","Hij wil niet.","werkwoordsvorm"),
 ("Jij loop te snel.","Jij loopt te snel.","werkwoordsvorm"),
 ("Wij hebt genoeg tijd.","Wij hebben genoeg tijd.","werkwoordsvorm"),
 ("Ik heeft honger.","Ik heb honger.","werkwoordsvorm"),
 ("De kinderen speelde buiten.","De kinderen speelden buiten.","meervoud verleden tijd"),
 ("Er zijn veel mensen die dat gelooft.","Er zijn veel mensen die dat geloven.","congruentie"),
 ("Hun hebben gelijk.","Zij hebben gelijk.","hun/zij"),
 ("Hun zeggen dat het regent.","Zij zeggen dat het regent.","hun/zij"),
 ("Hij is groter als ik.","Hij is groter dan ik.","als/dan"),
 ("Hij loopt sneller als zijn broer.","Hij loopt sneller dan zijn broer.","als/dan"),
 ("Ik heb liever koffie als thee.","Ik heb liever koffie dan thee.","als/dan"),
 ("Dit is jou boek.","Dit is jouw boek.","jou/jouw"),
 ("We gaan naar de museum.","We gaan naar het museum.","de/het"),
 ("We gaan naar de strand.","We gaan naar het strand.","de/het"),
 ("Het bedrijf heeft hun winst verhoogd.","Het bedrijf heeft zijn winst verhoogd.","verwijzing"),
 ("Ik eet graag pannekoeken.","Ik eet graag pannenkoeken.","tussen-n"),
 ("Ik ben naar huis gegaan omdat ik was moe.","Ik ben naar huis gegaan omdat ik moe was.","woordvolgorde"),
 ("Zij vertelde dat hij zou komen morgen.","Zij vertelde dat hij morgen zou komen.","woordvolgorde"),
 ("Omdat het regent, ik blijf thuis.","Omdat het regent, blijf ik thuis.","inversie"),
 ("Hij zei dat hij komt niet.","Hij zei dat hij niet komt.","woordvolgorde"),
 ("Ik heb mijn sleutels vergeten thuis.","Ik heb mijn sleutels thuis vergeten.","woordvolgorde"),
 ("Ze vroeg of dat ik kwam.","Ze vroeg of ik kwam.","of dat"),
 ("Ik weet niet wat dat hij bedoelt.","Ik weet niet wat hij bedoelt.","wat dat"),
 ("Het kost vijf euro's.","Het kost vijf euro.","meervoud munteenheid"),
 ("Ze heeft twee kinders.","Ze heeft twee kinderen.","meervoud"),
 ("Ik heb twee broer.","Ik heb twee broers.","meervoud"),
]
rows=[exact("schrijven",i,
  f"De volgende zin bevat precies één fout. Schrijf de volledige zin correct over, verander verder niets.\n\n{bad}",
  good, note) for i,(bad,good,note) in enumerate(CORR,1)]
write_exact("schrijven", rows)

# ============ Lezen: functional Dutch, native-written ========================
LEZEN = [
 ("Brief van de gemeente:\n“Vanaf 1 januari wordt het restafval om de twee weken opgehaald in plaats van wekelijks. Het gft-afval blijft wekelijks opgehaald worden.”\n\nHoe vaak wordt het restafval vanaf januari opgehaald?",
  "om de twee weken",["wekelijks","maandelijks","dat staat er niet"]),
 ("Bijsluiter:\n“Neem dit middel maximaal driemaal per dag in, met een tussenpoos van minstens vier uur. Niet gebruiken bij kinderen onder de zes jaar.”\n\nWat is de kortste toegestane tijd tussen twee doses?",
  "vier uur",["drie uur","zes uur","acht uur"]),
 ("Huurcontract:\n“De huur wordt jaarlijks per 1 juli verhoogd. De huurder ontvangt uiterlijk twee maanden van tevoren schriftelijk bericht.”\n\nVoor welke datum moet de verhoging uiterlijk zijn aangekondigd?",
  "1 mei",["1 juni","1 juli","1 september"]),
 ("Belastingdienst:\n“U moet uw aangifte inkomstenbelasting vóór 1 mei indienen. Vraagt u uitstel aan, dan krijgt u tot 1 september.”\n\nTot wanneer heeft iemand met uitstel de tijd?",
  "1 september",["1 mei","1 juli","31 december"]),
 ("NS:\n“Bij vertraging van meer dan 30 minuten heeft u recht op vergoeding: 50% van de ritprijs bij 30 tot 59 minuten, 100% bij 60 minuten of meer.”\n\nUw trein had 45 minuten vertraging. Op hoeveel vergoeding heeft u recht?",
  "50% van de ritprijs",["100% van de ritprijs","25% van de ritprijs","geen vergoeding"]),
 ("Werkgever:\n“Vakantiedagen die u dit jaar niet opneemt, vervallen op 1 juli van het volgende jaar.”\n\nWanneer vervallen de vakantiedagen van 2026?",
  "1 juli 2027",["31 december 2026","1 januari 2027","1 juli 2026"]),
 ("Zorgverzekeraar:\n“Het verplicht eigen risico bedraagt € 385 per jaar. Huisartsenzorg valt niet onder het eigen risico.”\n\nBetaalt u een bezoek aan de huisarts uit uw eigen risico?",
  "nee",["ja, volledig","ja, de helft","alleen boven € 385"]),
 ("Dienst Toeslagen:\n“U krijgt kinderopvangtoeslag alleen als beide ouders werken of een opleiding volgen.”\n\nEén ouder werkt, de andere ouder werkt niet en volgt geen opleiding. Krijgt dit gezin kinderopvangtoeslag?",
  "nee",["ja","alleen voor het eerste kind","alleen de helft"]),
 ("Gemeente:\n“Een bewonersparkeervergunning kost € 120 per jaar en geldt alleen in de eigen wijk. Een tweede vergunning op hetzelfde adres kost € 240.”\n\nWat betaalt een huishouden met twee vergunningen per jaar?",
  "€ 360",["€ 240","€ 120","€ 480"]),
 ("School:\n“De lessen beginnen om 8.30 uur. Leerlingen die na 8.45 uur binnenkomen, worden als te laat geregistreerd.”\n\nEen leerling komt om 8.40 uur binnen. Wordt zij als te laat geregistreerd?",
  "nee",["ja","alleen op maandag","dat hangt van de docent af"]),
 ("Apotheek:\n“Herhaalrecepten kunt u online bestellen; ze liggen na twee werkdagen voor u klaar.”\n\nU bestelt op vrijdag. Op welke dag ligt het recept op zijn vroegst klaar?",
  "dinsdag",["zaterdag","maandag","woensdag"]),
 ("Abonnement:\n“Het abonnement is maandelijks opzegbaar met een opzegtermijn van één maand.”\n\nU zegt op 10 maart op. Wanneer eindigt het abonnement?",
  "10 april",["10 maart","31 maart","1 mei"]),
 ("DigiD:\n“Uw activeringscode wordt per post verstuurd en is 20 dagen geldig na de verzenddatum.”\n\nDe code is op 1 april verzonden. Tot wanneer is hij geldig?",
  "21 april",["1 mei","20 april","30 april"]),
 ("Verkeersregels:\n“Binnen de bebouwde kom geldt een maximumsnelheid van 50 km/u, tenzij anders aangegeven. In een woonerf geldt stapvoets.”\n\nHoe hard mag u in een woonerf rijden?",
  "stapvoets",["50 km/u","30 km/u","70 km/u"]),
 ("Verhuizing:\n“U moet uw verhuizing binnen vijf dagen na de verhuisdatum doorgeven aan de gemeente waar u gaat wonen.”\n\nU verhuist op 3 juni. Wat is de uiterste dag om dit door te geven?",
  "8 juni",["3 juni","10 juni","1 juli"]),
]
rows=[mcq("lezen",i,p,c,d) for i,(p,c,d) in enumerate(LEZEN,1)]
write("lezen", rows)

# ============ KNM expansion + ONA ============================================
KNM2 = [
 ("Hoe heet het Nederlandse parlement als geheel?","de Staten-Generaal",["de Rijksraad","het Binnenhof","de Volksvertegenwoordiging"]),
 ("Wie is het staatshoofd van Nederland?","de koning",["de minister-president","de voorzitter van de Tweede Kamer","de commissaris van de Koning"]),
 ("Hoe vaak zijn er normaal gesproken Tweede Kamerverkiezingen?","om de vier jaar",["om de twee jaar","om de vijf jaar","elk jaar"]),
 ("Vanaf welke leeftijd mag je in Nederland stemmen?","18 jaar",["16 jaar","21 jaar","17 jaar"]),
 ("Wie kiest de leden van de Eerste Kamer?","de Provinciale Staten",["de kiezers rechtstreeks","de Tweede Kamer","de koning"]),
 ("Wie zit een gemeenteraadsvergadering voor?","de burgemeester",["de wethouder","de gemeentesecretaris","de commissaris van de Koning"]),
 ("Welk nummer bel je bij een levensbedreigende noodsituatie?","112",["0900-8844","911","144"]),
 ("Welk nummer bel je voor de politie als het geen spoed is?","0900-8844",["112","0800-1351","113"]),
 ("Vanaf welke leeftijd geldt de leerplicht?","5 jaar",["4 jaar","6 jaar","7 jaar"]),
 ("Waar staat de afkorting vmbo voor?","voorbereidend middelbaar beroepsonderwijs",["voortgezet middelbaar beroepsonderwijs","vrij middelbaar beroepsonderwijs","voorbereidend maatschappelijk beroepsonderwijs"]),
 ("Waar staat de afkorting cao voor?","collectieve arbeidsovereenkomst",["centrale arbeidsorganisatie","contractuele arbeidsovereenkomst","collectieve arbeidsorganisatie"]),
 ("Welke instantie betaalt de WW-uitkering uit?","het UWV",["de gemeente","de Belastingdienst","de SVB"]),
 ("Welke instantie betaalt de bijstandsuitkering uit?","de gemeente",["het UWV","de Belastingdienst","de SVB"]),
 ("Bij welke instantie vraag je huurtoeslag aan?","Dienst Toeslagen",["de gemeente","het UWV","de woningcorporatie"]),
 ("Binnen hoeveel dagen moet je een verhuizing doorgeven aan de gemeente?","vijf dagen",["één dag","tien dagen","dertig dagen"]),
 ("Waar staat de afkorting VvE voor?","Vereniging van Eigenaren",["Verbond van Verhuurders","Vereniging voor Eigendom","Verhuurdersvereniging"]),
 ("Waar schrijf je een nieuw bedrijf in?","bij de Kamer van Koophandel",["bij de Belastingdienst","bij de gemeente","bij het UWV"]),
 ("Wat is het standaardtarief van de btw in Nederland?","21%",["19%","9%","25%"]),
 ("Op welke dag wordt Prinsjesdag gehouden?","de derde dinsdag van september",["de eerste maandag van september","de derde donderdag van oktober","de laatste dinsdag van augustus"]),
 ("Hoe heet het Nederlandse volkslied?","het Wilhelmus",["de Watergeuzen","Wien Neêrlands Bloed","het Oranjelied"]),
 ("Welke vier steden vormen de kern van de Randstad?","Amsterdam, Rotterdam, Den Haag en Utrecht",["Amsterdam, Rotterdam, Eindhoven en Groningen","Amsterdam, Den Haag, Utrecht en Haarlem","Rotterdam, Den Haag, Leiden en Delft"]),
 ("Wat regelt artikel 1 van de Nederlandse Grondwet?","gelijke behandeling en het verbod op discriminatie",["de vrijheid van meningsuiting","het kiesrecht","de scheiding van kerk en staat"]),
 ("Welk orgaan is de hoogste bestuursrechter en adviseert de regering over wetgeving?","de Raad van State",["de Hoge Raad","de Eerste Kamer","de Nationale ombudsman"]),
 ("Wat regelt een waterschap?","het waterbeheer, zoals dijken en waterpeil",["de drinkwaterlevering aan huishoudens","de scheepvaart op rivieren","de visvergunningen"]),
 ("Wat is de rol van de huisarts in het Nederlandse zorgstelsel?","poortwachter: eerste aanspreekpunt en verwijzer naar specialisten",["spoedarts voor noodgevallen","tandarts voor het hele gezin","alleen arts voor kinderen"]),
 ("Wat betekent 'gedogen' in het Nederlandse bestuur?","iets officieel verboden toch toestaan zonder te vervolgen",["iets verplicht stellen","iets subsidiëren","iets uitstellen"]),
 ("Wat is de maximale proeftijd bij een arbeidscontract van meer dan twee jaar?","twee maanden",["één maand","drie maanden","zes maanden"]),
 ("Wat is de wettelijke opzegtermijn voor een werknemer?","één maand",["twee weken","twee maanden","drie maanden"]),
 ("Wat zijn de Deltawerken?","waterkeringen die Zuidwest-Nederland tegen de zee beschermen",["een reeks bruggen over de Rijn","de polders in Flevoland","de sluizen bij IJmuiden"]),
 ("Welke belastingdienstregeling verlaagt de belasting voor werkenden?","de arbeidskorting",["de zorgtoeslag","de kinderbijslag","de huurtoeslag"]),
]
extend("civics",[mcq("civics",200+i,p,c,d) for i,(p,c,d) in enumerate(KNM2,1)])

ONA = [
 ("Wat stuur je in Nederland gewoonlijk mee met een sollicitatie?","een cv en een motivatiebrief",["alleen een cv","een kopie van je paspoort","een verklaring omtrent het gedrag"]),
 ("Hoe spreek je een onbekende contactpersoon aan in een sollicitatiemail?","Geachte heer/mevrouw [achternaam]",["Hoi [voornaam]","Beste allemaal","Aan wie het aangaat, hallo"]),
 ("Wat doe je in Nederland op de eerste dag dat je ziek bent?","je meldt je bij je werkgever ziek",["je gaat naar de bedrijfsarts","je stuurt een doktersverklaring","je meldt het bij het UWV"]),
 ("Wat is een 'proeftijd'?","een periode aan het begin van een contract waarin beide partijen direct kunnen opzeggen",["een verplichte stage","de eerste maand zonder salaris","een periode met verlaagd loon"]),
 ("Wat betekent 'flexwerk'?","werk zonder vast contract of vaste uren",["thuiswerken","werken in ploegendienst","werk via een cao"]),
 ("Wat is een 'functioneringsgesprek'?","een gesprek over hoe het werk gaat en wat beter kan",["een sollicitatiegesprek","een ontslaggesprek","een salarisonderhandeling"]),
]
extend("register",[mcq("register",300+i,p,c,d,note="ONA") for i,(p,c,d) in enumerate(ONA,1)])
