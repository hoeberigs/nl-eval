from items_lib import mcq, extend, extend_exact

# ---------------------------------------------------------------- schrijven (exact)
P = "De volgende zin bevat precies één fout. Schrijf de volledige zin correct over, verander verder niets.\n\n"
S = [
 ("Ik heb teveel gegeten.", "Ik heb te veel gegeten.", "te veel los"),
 ("Waar ga je naar toe?", "Waar ga je naartoe?", "naartoe aaneen"),
 ("Ik spreek een beetje nederlands.", "Ik spreek een beetje Nederlands.", "taalnaam hoofdletter"),
 ("Het aantal ongelukken zijn gestegen.", "Het aantal ongelukken is gestegen.", "congruentie: het aantal is"),
 ("Ik weet niet of hij komt morgen.", "Ik weet niet of hij morgen komt.", "bijzin: werkwoord achteraan"),
 ("Omdat ik heb geen tijd, kom ik niet.", "Omdat ik geen tijd heb, kom ik niet.", "bijzin: werkwoord achteraan"),
 ("Gisteren ik ben naar Utrecht gegaan.", "Gisteren ben ik naar Utrecht gegaan.", "inversie na bijwoordelijke bepaling"),
 ("Dat is de auto wat ik wil kopen.", "Dat is de auto die ik wil kopen.", "betrekkelijk voornaamwoord: die"),
 ("Het huis wat we zagen, was te duur.", "Het huis dat we zagen, was te duur.", "betrekkelijk voornaamwoord: dat"),
 ("Ik vind dat hun gelijk hebben.", "Ik vind dat zij gelijk hebben.", "onderwerp: zij"),
 ("Zij is beter als haar zus.", "Zij is beter dan haar zus.", "vergrotende trap: dan"),
 ("Is dit jou fiets?", "Is dit jouw fiets?", "bezittelijk: jouw"),
 ("Dat is me broer.", "Dat is mijn broer.", "bezittelijk: mijn"),
 ("We gaan s'morgens vroeg weg.", "We gaan 's morgens vroeg weg.", "apostrof: 's morgens"),
 ("Ik heb drie fotos gemaakt.", "Ik heb drie foto's gemaakt.", "meervoud met apostrof"),
 ("Ze gaf een kado aan haar moeder.", "Ze gaf een cadeau aan haar moeder.", "spelling: cadeau"),
 ("Kom je zowiezo naar het feest?", "Kom je sowieso naar het feest?", "spelling: sowieso"),
 ("Dat was een grote verassing.", "Dat was een grote verrassing.", "spelling: verrassing"),
 ("Bel onmiddelijk de dokter.", "Bel onmiddellijk de dokter.", "spelling: onmiddellijk"),
 ("Hij was enigzins verbaasd.", "Hij was enigszins verbaasd.", "spelling: enigszins"),
 ("Het boek legt op tafel.", "Het boek ligt op tafel.", "liggen/leggen"),
 ("Ik ken morgen niet komen.", "Ik kan morgen niet komen.", "kennen/kunnen"),
 ("Hij heb een nieuwe baan.", "Hij heeft een nieuwe baan.", "vervoeging: heeft"),
 ("Wij hebben de koffie zetapparaat gekocht.", "Wij hebben het koffiezetapparaat gekocht.", "samenstelling aaneen; het-woord"),
 ("De pannekoeken waren lekker.", "De pannenkoeken waren lekker.", "tussen-n"),
 ("Ik ben hen adres kwijt.", "Ik ben hun adres kwijt.", "bezittelijk: hun"),
 ("Ze heeft het aan hun gegeven.", "Ze heeft het aan hen gegeven.", "na voorzetsel: hen"),
 ("Volgende week Maandag ben ik vrij.", "Volgende week maandag ben ik vrij.", "dagen kleine letter"),
 ("De vergadering is in Maart.", "De vergadering is in maart.", "maanden kleine letter"),
 ("Hij woont al tien jaar in den haag.", "Hij woont al tien jaar in Den Haag.", "plaatsnaam hoofdletters"),
 ("Ik heb u brief ontvangen.", "Ik heb uw brief ontvangen.", "bezittelijk: uw"),
 ("Wilt u mij de rekening opsturen alstublief?", "Wilt u mij de rekening opsturen alstublieft?", "spelling: alstublieft"),
 ("Zij heeft de hele dag gewerkd.", "Zij heeft de hele dag gewerkt.", "voltooid deelwoord: -t"),
 ("Ik word morgen 40 jaar en hij wordt 42.", "Ik word morgen 40 jaar en hij wordt 42.", None),
 ("De kinderen speelde buiten.", "De kinderen speelden buiten.", "verleden tijd meervoud"),
 ("Ik heb de trein gemist omdat ik was te laat.", "Ik heb de trein gemist omdat ik te laat was.", "bijzin: werkwoord achteraan"),
]
rows = []
n = 36
for wrong, right, note in S:
    if note is None:
        continue
    rows.append({"id": f"schrijven-{n:03d}", "category": "schrijven", "type": "exact", "prompt": P + wrong,
                 "answer": right, "note": note, "difficulty": "core"})
    n += 1
extend_exact("schrijven", rows)

# ---------------------------------------------------------------- KNM
K = [
 ("Op welke datum is Koningsdag?", "27 april", ["30 april", "5 mei", "27 maart"]),
 ("Wat gebeurt er op 4 mei om 20.00 uur?", "twee minuten stilte voor de oorlogsslachtoffers", ["het vuurwerk van Bevrijdingsdag", "de troonrede", "de intocht van Sinterklaas"]),
 ("Wanneer is Prinsjesdag?", "de derde dinsdag van september", ["de eerste dinsdag van oktober", "1 september", "de laatste vrijdag van september"]),
 ("Hoeveel zetels heeft de Tweede Kamer?", "150", ["75", "100", "225"]),
 ("Hoeveel provincies heeft Nederland?", "12", ["10", "11", "14"]),
 ("Welk orgaan beheert dijken en waterpeil?", "het waterschap", ["de provincie", "Rijkswaterstaat alleen", "de gemeente"]),
 ("Welk nummer belt u bij een niet-spoedeisende zaak voor de politie?", "0900-8844", ["112", "0800-1351", "14020"]),
 ("Tot welke leeftijd geldt de volledige leerplicht?", "16 jaar", ["12 jaar", "18 jaar", "21 jaar"]),
 ("Vanaf welke leeftijd moet iemand zelf een zorgverzekering hebben?", "18 jaar", ["16 jaar", "21 jaar", "vanaf de geboorte"]),
 ("Wie keert de kinderbijslag uit?", "de SVB", ["het UWV", "de Belastingdienst", "de gemeente"]),
 ("Bij welke instantie vraagt u een WW-uitkering aan?", "het UWV", ["de SVB", "de gemeente", "de Belastingdienst"]),
 ("Waar legt u het theorie- en praktijkexamen voor het rijbewijs af?", "bij het CBR", ["bij de RDW", "bij de gemeente", "bij de ANWB"]),
 ("Wat staat in artikel 1 van de Grondwet?", "gelijke behandeling en het verbod op discriminatie", ["de vrijheid van meningsuiting", "het kiesrecht", "de scheiding van kerk en staat"]),
 ("Welke stad is de hoofdstad en welke de regeringszetel?", "Amsterdam is de hoofdstad, Den Haag de regeringszetel", ["Den Haag is beide", "Amsterdam is beide", "Rotterdam is de hoofdstad, Den Haag de regeringszetel"]),
 ("Wat is de AOW?", "het staatspensioen vanaf de AOW-leeftijd", ["een uitkering bij werkloosheid", "een toeslag voor huurders", "de kinderbijslag"]),
 ("Wat is een BSN?", "het burgerservicenummer waarmee u bij de overheid bekend bent", ["een bankrekeningnummer", "een verzekeringsnummer", "een belastingnummer voor bedrijven"]),
 ("Waarvoor is een VOG nodig?", "voor werk waarbij een verklaring omtrent het gedrag wordt gevraagd, zoals in de kinderopvang", ["voor het openen van een bankrekening", "voor het aanvragen van DigiD", "voor het huren van een woning"]),
 ("Bij wie kan een huurder terecht bij een geschil over de huurprijs?", "de Huurcommissie", ["de Consumentenbond", "de politie", "het UWV"]),
 ("In welke maand betalen werkgevers meestal het vakantiegeld uit?", "mei", ["januari", "december", "juli"]),
 ("Hoe hoog is het vakantiegeld minimaal?", "8% van het brutoloon", ["5% van het brutoloon", "een dertiende maand", "10% van het nettoloon"]),
 ("Hoe lang mag de proeftijd maximaal duren bij een vast contract?", "twee maanden", ["één maand", "drie maanden", "zes maanden"]),
 ("Wat is de Deltawerken?", "een reeks waterkeringen in het zuidwesten na de watersnoodramp van 1953", ["een netwerk van snelwegen", "een tunnel onder het IJ", "een reeks windparken"]),
 ("Wat betekent NAP?", "Normaal Amsterdams Peil, het referentieniveau voor hoogtes", ["Nationaal Autoriteit Politie", "Nederlandse Arbeidsmarkt Pensioen", "een treinabonnement"]),
 ("Wie is de voorzitter van de ministerraad?", "de minister-president", ["de koning", "de voorzitter van de Tweede Kamer", "de vicepresident van de Raad van State"]),
 ("Wat is de OZB?", "een gemeentelijke belasting op onroerend goed", ["een belasting op auto's", "de omzetbelasting", "een toeslag voor ouderen"]),
 ("Vanaf welke leeftijd mag u stemmen bij de Tweede Kamerverkiezingen?", "18 jaar", ["16 jaar", "21 jaar", "17 jaar"]),
]
extend("civics", [mcq("civics", 55 + i, q, c, d, note="KNM") for i, (q, c, d) in enumerate(K)])

# ---------------------------------------------------------------- ONA en register
R = [
 ("Welke aanhef past in een sollicitatiebrief als de naam van de ontvanger onbekend is?", "Geachte heer, mevrouw,", ["Hoi,", "Beste mensen,", "Hallo allemaal,"]),
 ("Welke afsluiting past bij een formele brief die begint met “Geachte heer De Vries”?", "Met vriendelijke groet,", ["Doei,", "Groetjes,", "Liefs,"]),
 ("Welke vorm past in een e-mail aan een onbekende klant?", "Kunt u mij laten weten of dit schikt?", ["Kun je me laten weten of dit oké is?", "Laat ff weten of het lukt", "Zeg maar of het past"]),
 ("Wat is een loonstrook?", "een overzicht van bruto- en nettoloon en inhoudingen per periode", ["het arbeidscontract", "de jaaropgave van de bank", "een verklaring van goed gedrag"]),
 ("Wat is het verschil tussen bruto- en nettoloon?", "netto is wat overblijft na belasting en premies", ["bruto is wat overblijft na belasting", "er is geen verschil", "netto is inclusief vakantiegeld"]),
 ("Wat is een zzp'er?", "een zelfstandige zonder personeel", ["een werknemer met een tijdelijk contract", "een uitzendkracht", "een stagiair"]),
 ("Waar schrijft een zzp'er zich in?", "bij de Kamer van Koophandel", ["bij het UWV", "bij de gemeente", "bij de vakbond"]),
 ("Wat is een cao?", "een collectieve arbeidsovereenkomst voor een sector of bedrijf", ["een individueel contract", "een verzekering tegen ontslag", "een pensioenregeling"]),
 ("Wat doet de ondernemingsraad?", "medewerkers vertegenwoordigen bij besluiten van de werkgever", ["salarissen uitbetalen", "nieuwe medewerkers aannemen", "de boekhouding controleren"]),
 ("Wat is een functioneringsgesprek?", "een gesprek tussen werknemer en leidinggevende over het werk en de samenwerking", ["een sollicitatiegesprek", "een gesprek met de bedrijfsarts", "een ontslaggesprek"]),
 ("Wat is ouderschapsverlof?", "verlof om voor een jong kind te zorgen", ["verlof bij overlijden van een familielid", "verlof voor een verhuizing", "betaalde vakantie"]),
 ("Wat betekent “per direct beschikbaar” in een cv?", "de kandidaat kan meteen beginnen", ["de kandidaat werkt alleen overdag", "de kandidaat wil een vast contract", "de kandidaat heeft een opzegtermijn"]),
 ("Wat is een uitzendbureau?", "een bedrijf dat werknemers tijdelijk bij andere bedrijven plaatst", ["een verzekeraar", "een uitkeringsinstantie", "een opleidingsinstituut"]),
 ("Wat betekent “32 uur, fulltime is 40”?", "de functie is voor 80% van een volledige werkweek", ["u werkt 32 dagen per maand", "de functie is fulltime", "u werkt om de week"]),
 ("Welke zin is formeel genoeg voor een klacht aan een bedrijf?", "Ik verzoek u het bedrag binnen veertien dagen terug te storten.", ["Stort dat geld nou eens terug.", "Ik wil m'n geld terug, snel.", "Even terugstorten graag hè."]),
 ("Welke zin past bij een bericht aan een collega die u goed kent?", "Heb je even tijd om dit door te nemen?", ["Zou u zo vriendelijk willen zijn dit door te nemen?", "Hierbij verzoek ik u dit door te nemen.", "Gelieve dit door te nemen."]),
 ("Wat is een opzegtermijn?", "de periode tussen opzeggen en het einde van het contract", ["de proeftijd", "de duur van een tijdelijk contract", "de tijd tussen sollicitatie en gesprek"]),
 ("Wat betekent “bhv'er”?", "een bedrijfshulpverlener die bij nood eerste hulp verleent en evacueert", ["een beveiliger", "een bedrijfsarts", "een hoofd personeelszaken"]),
 ("Wat is een reiskostenvergoeding?", "een vergoeding van de werkgever voor woon-werkverkeer", ["een korting op de ov-chipkaart", "een belastingteruggave", "een uitkering van het UWV"]),
 ("Wat is een tijdelijk contract?", "een arbeidsovereenkomst met een einddatum", ["een contract zonder einddatum", "een contract via een uitzendbureau", "een contract voor zzp'ers"]),
 ("Waarvoor is de jaaropgave van de werkgever nodig?", "voor de belastingaangifte", ["voor het aanvragen van een rijbewijs", "voor de inschrijving bij de gemeente", "voor de zorgverzekering"]),
 ("Welke aanspreekvorm past bij een oudere buurvrouw die u niet goed kent?", "u", ["jij", "je", "jullie"]),
 ("Wat is de juiste volgorde in een sollicitatiebrief?", "aanhef, aanleiding, motivatie, afsluiting, groet", ["groet, motivatie, aanhef", "motivatie, aanhef, groet, aanleiding", "afsluiting, aanhef, motivatie"]),
 ("Wat is een “vaste aanstelling”?", "een contract voor onbepaalde tijd", ["een contract voor één jaar", "een oproepcontract", "een stagecontract"]),
]
extend("register", [mcq("register", 27 + i, q, c, d, note="ONA/register") for i, (q, c, d) in enumerate(R)])
