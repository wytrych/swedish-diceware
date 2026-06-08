#!/usr/bin/env python3
"""
Swedish blocklists for the Diceware pipeline.

  STOPWORDS  - function / closed-class words and high-frequency grammatical
               homographs that read as scaffolding (pronouns, prepositions,
               conjunctions, adverbs, modal/aux verb forms, determiners,
               numerals-as-words). Removed + logged as 'function_word'.

  PROFANITY  - (term, category) exact-match removals: svordomar, slurs,
               sexual/anatomical, violence/death, medical-distress, disgust,
               and high-ambiguity negative words. Logged with the category.

  PROFANITY_CONTAINS - strong offensive stems; any lemma CONTAINING one is
               removed (catches compounds). Kept deliberately small/precise.

These are seeds for a NATIVE-SPEAKER review, not a complete filter.
"""

# --- whitelist: good words wrongly caught by the fuzzy *_CONTAINS stems ------
# (checked before substring rules so they are never removed by a stem match)
WHITELIST = set("""
samordna samordning samordnad smord smördeg marknivå allsköns
sporra sporre trunk brunkol karusell okränkbar knivig potens
inskränka inskränkt smörkniv brödkniv impotent
""".split())

# --- function / closed-class words (surface forms) --------------------------
STOPWORDS = set("""
jag mig min mitt mina du dig din ditt dina han honom hans hon henne hennes
den det denna denne detta dess vi oss vår vårt våra ni er ert era de dem deras
sig sin sitt sina man en ett
någon något några nån nåt inga ingen inget all allt alla varje vart varenda
vilken vilket vilka sådan sådant sådana samma själv själva vem vad vems
hela helt halva
av i på till från med mot för om under över efter före genom mellan vid hos
åt ur utan inom utom bland kring runt längs enligt trots bakom framför ovanför
nedanför bredvid emot intill invid omkring per via
och eller men samt fast så att när då medan eftersom fastän ifall innan tills
både varken antingen ehuru emedan såvida liksom dvs
inte icke ej ju väl nog kanske alltid aldrig ofta ibland sällan redan ännu
snart strax nyss förut nu här där hit dit hem bort fram upp ner ned ut in
hemma borta inne ute uppe nere framme
ganska mycket lite litet mer mest mindre minst väldigt rätt alltför ytterst
precis exakt just bara endast enbart blott även också ock ändå dock däremot
alltså således därför därmed varför hur varifrån vartill annars istället
dessutom vidare nämligen således likaså desto ju
är var varit vore blir blev blivit bli blivande
har hade haft ha hav
kan kunde kunnat kunna ska skall skulle vill ville velat vilja
får fick fått få måste bör borde lär torde månne
göra gör gjorde gjort
komma kom kommit kommer
säga sa sade sagt säger
en ett två tre fyra fem sex sju åtta nio tio elva tolv
första andra tredje fjärde femte sjätte
""".split())

# --- profanity / negative-connotation exact removals ------------------------
PROFANITY = {
    # svordomar / general vulgar
    "fan": "svordom", "jävel": "svordom", "jävla": "svordom", "jävlar": "svordom",
    "helvete": "svordom", "satan": "svordom", "djävul": "svordom",
    "djävel": "svordom", "förbannad": "svordom", "förbaskad": "svordom",
    "skit": "svordom", "skita": "svordom", "skitig": "svordom",
    "as": "svordom", "aspackad": "svordom",
    "idiot": "nedsättande", "pucko": "nedsättande", "kräk": "nedsättande",
    "imbecill": "nedsättande", "debil": "nedsättande", "efterbliven": "nedsättande",
    "dåre": "nedsättande", "fåntratt": "nedsättande",
    # slurs / derogatory identity
    "neger": "slur", "blatte": "slur", "svartskalle": "slur", "zigenare": "slur",
    "bög": "slur", "flata": "slur", "fjolla": "slur", "mongo": "slur",
    "cp": "slur", "pack": "slur",
    # sexual / anatomical
    "kuk": "sexuellt", "fitta": "sexuellt", "snopp": "sexuellt",
    "snippa": "sexuellt", "kåt": "sexuellt", "knull": "sexuellt",
    "knulla": "sexuellt", "runka": "sexuellt", "hora": "sexuellt",
    "sköka": "sexuellt", "slyna": "sexuellt", "balle": "sexuellt",
    "pung": "sexuellt", "samlag": "sexuellt", "orgasm": "sexuellt",
    "penis": "sexuellt", "vagina": "sexuellt", "slida": "sexuellt",
    "klitoris": "sexuellt", "testikel": "sexuellt", "anus": "sexuellt",
    "röv": "sexuellt", "arsle": "sexuellt", "arsel": "sexuellt",
    "prostituerad": "sexuellt", "porr": "sexuellt", "dildo": "sexuellt",
    # violence / death / weapons
    "död": "vald", "döda": "vald", "döende": "vald", "mord": "vald",
    "mörda": "vald", "mördare": "vald", "dräpa": "vald", "dråp": "vald",
    "våld": "vald", "våldta": "vald", "våldtäkt": "vald",
    "misshandel": "vald", "tortyr": "vald", "tortera": "vald",
    "blod": "vald", "blodig": "vald", "lik": "vald", "kadaver": "vald",
    "vapen": "vald", "kniv": "vald", "dolk": "vald", "gevär": "vald",
    "pistol": "vald", "revolver": "vald", "bomb": "vald", "granat": "vald",
    "krig": "vald", "slakt": "vald", "slakta": "vald", "kväva": "vald",
    "strypa": "vald", "avrätta": "vald", "massaker": "vald", "terror": "vald",
    "terrorist": "vald", "gisslan": "vald", "mina": "vald",
    "sprängämne": "vald", "hänga": "vald", "galge": "vald",
    "hat": "vald", "hata": "vald", "mobba": "vald", "mobbning": "vald",
    # medical-distress / illness
    "cancer": "medicinskt", "tumör": "medicinskt", "sjukdom": "medicinskt",
    "sjuk": "medicinskt", "pest": "medicinskt", "kolera": "medicinskt",
    "smitta": "medicinskt", "plåga": "medicinskt", "smärta": "medicinskt",
    "lidande": "medicinskt", "ångest": "medicinskt", "panik": "medicinskt",
    "depression": "medicinskt", "självmord": "medicinskt",
    "självskada": "medicinskt", "demens": "medicinskt", "stroke": "medicinskt",
    "infarkt": "medicinskt", "blödning": "medicinskt", "blöda": "medicinskt",
    "kräkas": "medicinskt", "böld": "medicinskt", "förgifta": "medicinskt",
    "kräfta": "medicinskt",
    # disgust / bodily
    "bajs": "äckel", "bajsa": "äckel", "kiss": "äckel", "kissa": "äckel",
    "piss": "äckel", "pissa": "äckel", "snor": "äckel", "snorig": "äckel",
    "spya": "äckel", "kräks": "äckel", "diarré": "äckel", "dynga": "äckel",
    "träck": "äckel", "avföring": "äckel", "urin": "äckel", "snusk": "äckel",
    "mög": "äckel", "var": "äckel",
    # crime / negative (ambiguous-but-better-flagged)
    "tjuv": "negativt", "stöld": "negativt", "stjäla": "negativt",
    "rån": "negativt", "råna": "negativt", "bedragare": "negativt",
    "fängelse": "negativt", "straff": "negativt", "lögn": "negativt",
    "ljuga": "negativt", "svika": "negativt",
}

# --- strong offensive stems (substring match catches compounds) -------------
# Chosen to keep false positives low; ambiguous stems (sex=six, brott=fracture,
# hat=hatt, röv=erövra, rån=wafer, kväv=kväve) are handled via exact compounds.
PROFANITY_CONTAINS = {
    # sexual
    "knull": "sexuellt", "pedofil": "sexuellt", "incest": "sexuellt",
    "porr": "sexuellt", "kåt": "sexuellt", "onani": "sexuellt",
    "runk": "sexuellt", "dildo": "sexuellt", "samlag": "sexuellt",
    "orgasm": "sexuellt", "köns": "sexuellt",
    # violence / death / weapons
    "våldta": "vald", "våldtäkt": "vald", "mord": "vald", "mörd": "vald",
    "död": "vald", "bomb": "vald", "vapen": "vald", "terror": "vald",
    "tortyr": "vald", "massaker": "vald", "kniv": "vald", "gevär": "vald",
    "pistol": "vald", "granat": "vald", "krig": "vald", "dråp": "vald",
    "misshandel": "vald", "avrätt": "vald", "galg": "vald", "våld": "vald",
    # medical / STD
    "cancer": "medicinskt", "tumör": "medicinskt", "klamydia": "medicinskt",
    "herpes": "medicinskt", "syfilis": "medicinskt", "gonorr": "medicinskt",
    "venerisk": "medicinskt",
    # disgust
    "bajs": "äckel", "piss": "äckel", "knark": "negativt",
    # extremism
    "nazis": "negativt", "fascis": "negativt",
}

# --- nationalities / languages / demonyms / place-region (proper-adjacent) --
# Per spec: drop place/region names. Curated to avoid common -isk adjectives
# (magisk, logisk, fisk, frisk, viska, diska ... are NOT here on purpose).
NATIONALITY = set("""
svensk svenska osvensk nysvensk nysvenska allsvensk
norsk norska dansk danska finsk finska finländsk
tysk tyska engelsk engelska brittisk brittiska
fransk franska spansk spanska italiensk italienska
portugisisk portugisiska holländsk holländska belgisk belgiska
grekisk grekiska latinsk romersk
rysk ryska ryss vitrysk vitryska ukrainsk ukrainska
polsk polska tjeckisk tjeckiska ungersk ungerska
estnisk estniska lettisk lettiska litauisk litauiska
serbisk serbiska kroatisk kroatiska
amerikansk amerikanska amerikan afrikansk afrikan
asiatisk asiatiska asiat europeisk europé
arabisk arabiska arab persisk persiska iransk iranska
turkisk turkiska kurd kurder kurdisk kurdiska
indisk indiska kinesisk kinesiska japansk japanska
egyptisk egyptiska etiopisk etiopiska syrisk syriska
irakisk irakiska assyriska arameiska hebreisk hebreiska
somalier somalisk koptisk koptiska
keltisk keltiska gotisk gotiska baskisk baskiska
nordisk skandinavisk germansk slavisk slav arisk
isländsk isländska irländsk irländska
gotländsk småländsk åländsk
pakistan bokmål nynorsk esperanto latin swahili jiddisch
""".split())

# safe substring stems for negative derived forms (low false-positive)
NEGATIVE_CONTAINS = {
    "avund": "negativt", "sårbar": "negativt", "olyck": "negativt",
    "katastrof": "negativt", "lögn": "negativt", "kränk": "negativt",
    "förtryck": "negativt", "vansinn": "negativt", "plågsam": "negativt",
    "smärtsam": "negativt", "straff": "negativt", "bedräg": "negativt",
    "misslyck": "negativt", "fördärv": "negativt", "förödel": "negativt",
    "eländ": "negativt", "misär": "negativt", "fiasko": "negativt",
    "judehat": "negativt", "mobb": "negativt", "fördom": "negativt",
    "fördöm": "negativt", "grymhet": "negativt", "galenskap": "negativt",
    "otäck": "negativt", "vidrig": "negativt", "usel": "negativt",
    # military / coercion (auto-sweep 2) — checked for low false-positive
    "militär": "vald", "soldat": "vald", "infanteri": "vald",
    "artilleri": "vald", "kavalleri": "vald", "invasion": "vald",
    "ockup": "vald", "plundr": "vald", "anfall": "vald",
    "tving": "negativt", "tvång": "negativt", "deport": "negativt",
    "kidnapp": "negativt", "slaveri": "negativt", "anklag": "negativt",
    "arrest": "negativt", "vräk": "negativt", "ruin": "negativt",
    "epidem": "medicinskt", "pandem": "medicinskt", "trauma": "medicinskt",
}

# military / war-machine, coercion/legal-distress, medical-distress (sweep 2)
MILITARY = set("""
amiral attack beskjuta beväpnad obeväpnad bunker fästning general
krut löjtnant slagfält strid trupp belägring fälttåg stridsvagn
""".split())

MEDICAL_EXTRA = set("""
astma chock epilepsi koma karantän mens migrän svimma värk yrsel
huvudvärk nackspärr siemens infektion infektera infekterad
illamående svindel förlamning
""".split())

GENITIVE = set("världens dagens".split())

# --- religious vocabulary (user: remove ALL religious vocab) -----------------
RELIGION = set("""
islam islamisk islamism muslim muslimsk
kristen kristendom kristlig kristlig kristelig
katolik katolsk protestant ortodox frikyrklig kyrklig
jude judisk judendom hindu hinduisk hinduism
buddha buddhism buddhist sikh
präst prästerlig pastor biskop ärkebiskop kardinal påve
nunna munk abbot kloster diakon
kyrka domkyrka katedral kapell moské synagoga tempel altare
predika predikan predikant gudstjänst mässa
psalm psalmbok bibel biblisk koran evangelium evangelisk
gud gudinna gudomlig gudfruktig avgud
helig helga helgon helgd helgon martyr
synd syndig synda syndare frälsa frälsning frälsare
välsigna välsignelse bön välsignad
profet apostel lärjunge dop döpa nattvard sakrament
pilgrim sabbat advent gudlös hednisk hedning avguderi
treenighet uppståndelse skärseld
""".split())

# --- negative-connotation sweep (user: remove ALL negative) ------------------
NEGATIVE = set("""
usel urusel uselt ynklig ömklig jämmerlig eländig bedrövlig
miserabel futtig patetisk vidrig äcklig motbjudande frånstötande
vämjelig avskyvärd vedervärdig förskräcklig ryslig fasansfull
hemsk otäck kuslig olustig obehaglig olycksbådande hotfull skrämmande
elak gemen lömsk feg lat slö enfaldig fånig fjantig larvig töntig
fånig korkad inskränkt trångsynt
apatisk hysterisk manisk neurotisk paranoid deprimerad
dyster trist glåmig grinig sur vresig butter ilsken
arg rasande ursinnig uppretad irriterad frustrerad uppgiven
besviken missnöjd olycklig sorgsen bedrövad förtvivlad
hopplös modlös vanmäktig maktlös hjälplös
värdelös meningslös gagnlös fruktlös lönlös sårbar bräcklig skröplig
omoralisk oärlig ohederlig skamlös hänsynslös samvetslös skoningslös
obarmhärtig grym brutal skändlig nedrig usling skurk bov
elände misär vånda kval pina vedermöda
fiasko misslyckande motgång bakslag besvikelse förödelse
oro rädsla skräck fasa fruktan förtvivlan vanmakt hopplöshet
ensamhet saknad tomhet vemod ilska vrede ursinne raseri
agg avsky förakt vämjelse äckel motvilja avsmak
fanatism fanatiker dårskap galenskap vansinne vanvett
fördärv undergång ruin kollaps mardröm
ondska grymhet brutalitet vidrighet styggelse skändlighet
oförrätt orättvisa förtryck övergrepp kränkning förnedring
förödmjukelse skam skuld ånger samvetskval blygsel
avsky förakta kvälja äckla sarga
bråka gräla kivas träta trakassera förfölja hota skrämma
terrorisera lura bedra förråda sabotera förstöra fördärva
krossa skövla plundra härja förgöra
gnälla klaga jämra sucka snyfta tjuta vråla
misslyckas förlora kvävas förgås lida plågas våndas
frukta ängslas sörja ångra skämmas blygas
dispyt tvist gräl bråk konflikt fejd osämja split
avundsjuk avund missunnsam hämndlysten skadeglad
krångla krånglig besvärlig knepig kärv
skrynklig spydig hånfull föraktfull nedlåtande arrogant högfärdig
svek svikare sviken förrädare förräderi skamfläck skuldsatt
galen grymt elaka elakhet elakartad oskuld bestraffa avskräcka hotande
hotfull hotelse hotbild felaktig fördömande
fängsla fördriva kuva betvinga underkuva förslava utvisning
bödel dömd häkta konkurs laglöshet razzia utmätning åtal åtala husarrest
""".split())

# --- exact compounds for ambiguous stems we can't safely substring-match -----
PROFANITY_EXACT_EXTRA = {
    "analsex": "sexuellt", "oralsex": "sexuellt", "sexbrott": "sexuellt",
    "sexköp": "sexuellt", "sexslav": "sexuellt", "sexliv": "sexuellt",
    "sexlust": "sexuellt", "sexism": "sexuellt", "sexig": "sexuellt",
    "sexuell": "sexuellt", "bisexuell": "sexuellt", "homosexuell": "sexuellt",
    "heterosexuell": "sexuellt", "naken": "sexuellt", "naket": "sexuellt",
    "nakenhet": "sexuellt", "lesbisk": "sexuellt", "erotisk": "sexuellt",
    "kukhuvud": "sexuellt", "rövhål": "sexuellt", "kåthet": "sexuellt",
    "aids": "medicinskt", "impotens": "medicinskt", "horunge": "slur",
    "sexistisk": "sexuellt", "nakenbad": "sexuellt", "horribel": "negativt",
    "hatbrott": "vald", "ekobrott": "negativt", "mutbrott": "negativt",
    "lagbrott": "negativt", "inbrott": "negativt", "mordbrand": "vald",
    "benbrott": "medicinskt", "magsår": "medicinskt", "skavsår": "medicinskt",
    "hudcancer": "medicinskt", "magsjuka": "medicinskt", "sjösjuka": "medicinskt",
    "åksjuk": "medicinskt", "sjuklig": "medicinskt", "dödläge": "vald",
    "kvävning": "vald", "tårgas": "vald", "kulspruta": "vald",
    "rövare": "negativt", "rånare": "negativt", "rånförsök": "negativt",
    "biltjuv": "negativt", "tjuvjakt": "negativt", "stöldgods": "negativt",
    "näthat": "negativt", "hatisk": "negativt", "hatare": "negativt",
    "hatande": "negativt", "hatobjekt": "negativt", "fylleri": "negativt",
    "bakfylla": "negativt", "fyllo": "negativt", "berusad": "negativt",
}
