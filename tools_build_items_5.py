from items_lib import mcq, extend

# ---------------------------------------------------------------- diminutives
D = [
 ("raam","raampje",["raamje","raammetje"]),("zon","zonnetje",["zontje","zonetje"]),("pan","pannetje",["pantje","panetje"]),
 ("brug","bruggetje",["brugje","brugtje"]),("kar","karretje",["kartje","karetje"]),("koning","koninkje",["koningje","koningetje"]),
 ("ding","dingetje",["dinkje","dingje"]),("ei","eitje",["eietje","eitjes"]),("kip","kippetje",["kipje","kipetje"]),
 ("vlag","vlaggetje",["vlagje","vlagetje"]),("auto","autootje",["autotje","auto'tje"]),("café","cafeetje",["cafétje","cafeetje's"]),
 ("paraplu","parapluutje",["paraplutje","paraplu'tje"]),("foto","fotootje",["foto'tje","fototje"]),("baby","baby'tje",["babytje","babietje"]),
 ("taxi","taxietje",["taxi'tje","taxitje"]),("bureau","bureautje",["bureauutje","bureau'tje"]),("lam","lammetje",["lampje","lamje"]),
 ("arm","armpje",["armetje","armje"]),("film","filmpje",["filmetje","filmje"]),("weg","weggetje",["wegje","wegtje"]),
 ("pad","paadje",["padje","paddetje"]),("gat","gaatje",["gatje","gattetje"]),("schip","scheepje",["schipje","schippetje"]),
 ("glas","glaasje",["glasje","glassetje"]),("blad","blaadje",["bladje","bladdetje"]),("spel","spelletje",["speltje","spelje"]),
 ("ster","sterretje",["stertje","steretje"]),("wagen","wagentje",["wagenetje","wagenje"]),("deken","dekentje",["dekenetje","dekentje's"]),
]
extend("diminutives", [mcq("diminutives", 19+i, f"Wat is het verkleinwoord van “{w}”?", c, d, note="verkleinwoord") for i,(w,c,d) in enumerate(D)])

# ---------------------------------------------------------------- word order
W = [
 ("Ik weet dat ___.", "hij morgen komt", ["hij komt morgen", "morgen hij komt"]),
 ("Morgen ___ naar Rotterdam.", "ga ik", ["ik ga", "ga naar ik"]),
 ("Hij zegt dat ___.", "hij het boek gelezen heeft", ["hij heeft gelezen het boek", "heeft hij het boek gelezen"]),
 ("Ik heb ___ gebeld.", "gisteren mijn moeder", ["mijn moeder gisteren", "gisteren aan mijn moeder"]),
 ("Zij ___ elke dag om zeven uur ___.", "staat … op", ["opstaat … ", "staat op … "]),
 ("Omdat het regent, ___.", "blijven we thuis", ["we blijven thuis", "blijven thuis we"]),
 ("Ik ga ___ naar het station.", "morgen met de fiets", ["met de fiets morgen", "naar morgen met de fiets"]),
 ("Kun je ___?", "het raam even dichtdoen", ["even dichtdoen het raam", "dichtdoen het raam even"]),
 ("Hij heeft ___.", "de hele dag hard gewerkt", ["hard gewerkt de hele dag", "de hele dag gewerkt hard"]),
 ("Ik weet niet ___.", "waar hij woont", ["waar woont hij", "hij waar woont"]),
 ("Als je tijd hebt, ___.", "kom dan even langs", ["dan kom even langs", "kom even dan langs"]),
 ("Ze heeft gezegd ___.", "dat ze niet kan komen", ["dat ze kan niet komen", "dat kan ze niet komen"]),
 ("___ je vanavond?", "Kom", ["Komt", "Kom jij"]),
 ("Ik wil ___.", "graag een kop koffie", ["een kop koffie graag drinken", "graag drinken een kop koffie"]),
 ("Hij ___ zijn sleutels ___.", "is … kwijt", ["kwijt … is", "is kwijt … "]),
 ("Toen ik thuiskwam, ___.", "was hij al weg", ["hij was al weg", "was al weg hij"]),
 ("Ik probeer ___.", "elke dag te lezen", ["te lezen elke dag", "elke dag lezen te"]),
 ("Zij vertelde ___.", "me gisteren een verhaal", ["gisteren me een verhaal", "een verhaal me gisteren"]),
 ("Waarom ___?", "ben je niet gekomen", ["je bent niet gekomen", "ben niet je gekomen"]),
 ("Ik denk ___.", "dat het morgen gaat regenen", ["dat het gaat morgen regenen", "dat morgen gaat het regenen"]),
 ("Hij belt ___.", "zijn zus elke zondag op", ["op zijn zus elke zondag", "elke zondag op zijn zus"]),
 ("We hebben ___.", "in Utrecht een huis gekocht", ["gekocht een huis in Utrecht", "een huis gekocht in Utrecht al"]),
 ("Nadat we gegeten hadden, ___.", "gingen we wandelen", ["we gingen wandelen", "gingen wandelen we"]),
 ("Ik heb hem ___.", "niet gezien", ["gezien niet", "niet zien gedaan"]),
 ("Mag ik ___?", "even iets vragen", ["iets even vragen", "vragen even iets"]),
 ("Zij ___ altijd ___.", "komt … te laat", ["te laat … komt", "komt te laat … "]),
 ("Hoewel hij moe was, ___.", "werkte hij door", ["hij werkte door", "werkte door hij"]),
 ("Ik heb geen zin ___.", "om vanavond te koken", ["om te koken vanavond", "vanavond om te koken"]),
]
extend("word_order", [mcq("word_order", 23+i, f"Welke aanvulling geeft de juiste woordvolgorde?\n\n{s}", c, d, note="woordvolgorde") for i,(s,c,d) in enumerate(W)])

# ---------------------------------------------------------------- variants (NL / BE)
V = [
 ("kuisen","schoonmaken",["koken","kussen"]),("goesting","zin",["honger","haast"]),("nonkel","oom",["neef","opa"]),
 ("camion","vrachtwagen",["bestelbus","tractor"]),("kleed","jurk",["tapijt","jas"]),("ajuin","ui",["knoflook","prei"]),
 ("confituur","jam",["stroop","pindakaas"]),("appelsien","sinaasappel",["appel","citroen"]),("zetel","bank",["stoel","kruk"]),
 ("zwemkom","zwembad",["badkuip","vijver"]),("kot","studentenkamer",["schuur","kantine"]),("solden","uitverkoop",["belasting","salaris"]),
 ("stylo","pen",["potlood","stift"]),("valies","koffer",["rugzak","tas"]),("proper","schoon",["netjes","nieuw"]),
 ("vijs","schroef",["spijker","bout"]),("schepen","wethouder",["burgemeester","raadslid"]),("bomma","oma",["tante","moeder"]),
 ("plezant","leuk",["duur","druk"]),("gsm","mobiele telefoon",["laptop","tablet"]),
]
extend("variants", [mcq("variants", 21+i, f"Welk woord gebruikt men in Nederland voor het Belgisch-Nederlandse “{b}”?", c, d, note="variant NL/BE") for i,(b,c,d) in enumerate(V)])

# ---------------------------------------------------------------- formatting
F = [
 ("Hoe schrijft u het bedrag twaalf euro vijftig in een brief?", "€ 12,50", ["€ 12.50", "12,50 €", "€12,5"]),
 ("Hoe schrijft u het getal tienduizend met scheidingsteken?", "10.000", ["10,000", "10 000,", "10'000"]),
 ("Welke schrijfwijze van de datum is in een formele brief gebruikelijk?", "12 maart 2026", ["maart 12, 2026", "12 Maart 2026", "12/3 2026"]),
 ("Hoe wordt een tijdstip in lopende tekst geschreven?", "om 14.30 uur", ["om 14h30", "om 2.30 pm", "om 14u30"]),
 ("Waar staat “t/m” voor?", "tot en met", ["tot met", "tijdens en met", "tussen en met"]),
 ("Waar staat “i.v.m.” voor?", "in verband met", ["in vergelijking met", "in verhouding met", "in verwachting met"]),
 ("Waar staat “n.a.v.” voor?", "naar aanleiding van", ["na afloop van", "namens allen van", "niet aanwezig vanaf"]),
 ("Waar staat “z.o.z.” voor?", "zie ommezijde", ["zonder omhaal zeggen", "zie onderaan zin", "zo ook zij"]),
 ("Hoe schrijft u een Nederlandse postcode?", "1234 AB", ["1234AB", "AB 1234", "12-34 AB"]),
 ("Hoe wordt vijf procent in lopende tekst geschreven?", "5 procent of 5%", ["5 %", "5pct", "vijf-procent"]),
 ("Welke afkorting gebruikt u voor “mevrouw” in een adressering?", "mw.", ["mvr.", "mev.", "mrs."]),
 ("Hoe schrijft u een Nederlands mobiel nummer?", "06-12345678", ["+31 (0) 612345678.", "06 12 34 56 78 9", "0612-345-678"]),
 ("Welke schrijfwijze is correct?", "de 21e eeuw", ["de 21ste eeuw", "de 21-e eeuw", "de 21e Eeuw"]),
 ("Hoe schrijft u “bijvoorbeeld” afgekort?", "bijv.", ["b.v.", "bv.", "bijvb."]),
 ("Hoe schrijft u het rangtelwoord “eerste” met een cijfer?", "1e", ["1ste", "1st", "1é"]),
 ("Waar staat “o.a.” voor?", "onder andere", ["onder aan", "of anders", "op afspraak"]),
 ("Welke schrijfwijze van een IBAN is gebruikelijk?", "NL91 ABNA 0417 1643 00", ["NL91ABNA0417164300 ", "NL 91 ABNA 04171643 00", "NL-91-ABNA-0417-1643-00"]),
 ("Hoe schrijft u een bedrag zonder centen?", "€ 250,-", ["€ 250.00", "€ 250,0", "250 €,-"]),
 ("Hoe schrijft u “doctorandus” als titel voor een naam?", "drs.", ["Drs.", "dr.", "drs"]),
 ("Waar staat “d.w.z.” voor?", "dat wil zeggen", ["dus wij zeggen", "daarom wel zo", "dat was zo"]),
]
extend("formatting", [mcq("formatting", 21+i, q, c, d, note="notatieconventie") for i,(q,c,d) in enumerate(F)])

# ---------------------------------------------------------------- idioms
I = [
 ("Wat betekent “de kat uit de boom kijken”?", "afwachten hoe iets zich ontwikkelt", ["een huisdier zoeken", "naar boven kijken", "iets snel beslissen"]),
 ("Wat betekent “met de deur in huis vallen”?", "meteen ter zake komen", ["onaangekondigd op bezoek komen", "struikelen bij binnenkomst", "een ongeluk hebben"]),
 ("Wat betekent “iets onder de knie hebben”?", "iets goed beheersen", ["iets verstoppen", "pijn hebben", "iets vergeten"]),
 ("Wat betekent “de hond in de pot vinden”?", "te laat komen voor het eten", ["een huisdier kopen", "een lekkere maaltijd krijgen", "een verrassing vinden"]),
 ("Wat betekent “het regent pijpenstelen”?", "het regent heel hard", ["het hagelt", "het regent zachtjes", "het gaat opklaren"]),
 ("Wat betekent “iemand in de maling nemen”?", "iemand voor de gek houden", ["iemand helpen", "iemand ontslaan", "iemand bedanken"]),
 ("Wat betekent “de koe bij de horens vatten”?", "een probleem aanpakken", ["een boerderij bezoeken", "gevaarlijk werk doen", "iets uitstellen"]),
 ("Wat betekent “water bij de wijn doen”?", "een compromis sluiten", ["een feest vieren", "zuinig zijn", "iets verdunnen"]),
 ("Wat betekent “de boot missen”?", "een kans mislopen", ["te laat op de veerboot zijn", "verdwalen", "een afspraak vergeten"]),
 ("Wat betekent “een appeltje voor de dorst”?", "spaargeld voor later", ["een gezonde snack", "een klein cadeau", "een drankje"]),
 ("Wat betekent “het hoofd boven water houden”?", "financieel net rondkomen", ["leren zwemmen", "trots zijn", "hard nadenken"]),
 ("Wat betekent “ergens een punt achter zetten”?", "met iets stoppen", ["iets afronden met een zin", "iets uitstellen", "iets herhalen"]),
 ("Wat betekent “de plank misslaan”?", "het helemaal mis hebben", ["een klus verprutsen", "iets vergeten", "te hard werken"]),
 ("Wat betekent “een oogje in het zeil houden”?", "opletten, in de gaten houden", ["gaan zeilen", "iets negeren", "een compliment geven"]),
 ("Wat betekent “nu komt de aap uit de mouw”?", "nu wordt de ware reden duidelijk", ["nu wordt het gezellig", "nu gaat het mis", "nu is het te laat"]),
 ("Wat betekent “iemand iets op de mouw spelden”?", "iemand iets wijsmaken", ["iemand een cadeau geven", "iemand bedanken", "iemand aanraken"]),
 ("Wat betekent “het is koek en ei”?", "ze kunnen het goed met elkaar vinden", ["het is ontbijttijd", "het is gemakkelijk", "het is ingewikkeld"]),
 ("Wat betekent “door de mand vallen”?", "ontmaskerd worden", ["een ongeluk krijgen", "slagen voor een examen", "afvallen"]),
 ("Wat betekent “de kogel is door de kerk”?", "de beslissing is genomen", ["er is een ongeluk gebeurd", "het feest is begonnen", "de discussie begint"]),
 ("Wat betekent “iets met een korreltje zout nemen”?", "iets niet al te serieus nemen", ["iets zouter maken", "iets goed onthouden", "iets zorgvuldig lezen"]),
]
extend("idioms", [mcq("idioms", 33+i, q, c, d, note="uitdrukking") for i,(q,c,d) in enumerate(I)])

# ---------------------------------------------------------------- false friends
FF = [
 ("Wat betekent het Nederlandse “eventueel”?", "mogelijk, indien nodig", ["uiteindelijk", "gelijk", "toevallig"]),
 ("Wat betekent het Nederlandse “brutaal”?", "onbeschaamd", ["gewelddadig", "eerlijk", "moedig"]),
 ("Wat betekent het Nederlandse “slim”?", "intelligent", ["dun", "traag", "glad"]),
 ("Wat betekent het Nederlandse “gift”?", "een schenking", ["vergif", "een cadeau dat je krijgt bij een bruiloft", "een talent"]),
 ("Wat betekent het Nederlandse “monster” in een winkel?", "een proefexemplaar", ["een gedrocht", "een korting", "een klacht"]),
 ("Wat betekent het Nederlandse “map”?", "een omslag voor papieren", ["een landkaart", "een plattegrond", "een lijst"]),
 ("Wat betekent het Nederlandse “mening”?", "opvatting", ["betekenis", "bedoeling", "gedachte aan iets"]),
 ("Wat betekent het Nederlandse “doof”?", "niet kunnen horen", ["dom", "stom", "doorzichtig"]),
 ("Wat betekent het Nederlandse “durven”?", "de moed hebben", ["mogen", "moeten", "willen"]),
 ("Wat betekent het Nederlandse “bellen”?", "telefoneren", ["blaffen", "luiden", "roepen"]),
 ("Wat betekent het Nederlandse “tafel”?", "meubelstuk om aan te eten", ["schoolbord", "plank", "lijst"]),
 ("Wat betekent het Nederlandse “winkel”?", "een zaak waar je koopt", ["een hoek", "een knipoog", "een kraam"]),
 ("Wat betekent het Nederlandse “rok”?", "een kledingstuk voor het onderlichaam", ["een jas", "een muziekstijl", "een steen"]),
 ("Wat betekent het Nederlandse “zee”?", "grote watermassa, zoals de Noordzee", ["een meer", "een rivier", "een zee van tijd"]),
]
extend("false_friends", [mcq("false_friends", 27+i, q, c, d, note="valse vriend") for i,(q,c,d) in enumerate(FF)])
