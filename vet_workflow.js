export const meta = {
  name: 'sv-diceware-vetting',
  description: 'Iteratively vet the Swedish Diceware list with fan-out agents until convergence (file-based)',
  phases: [
    { title: 'Build' },
    { title: 'Vet' },
  ],
}

// Repo directory the build runs in. Defaults to the current working directory
// (launch the workflow from the repo root); override with args.dir if needed.
const DIR = (typeof args === 'object' && args && args.dir) || '.'
const CHUNK = 150
const MAX_ROUNDS = 20

const MAINT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    applied: { type: 'integer' },
    numNew: { type: 'integer' },
    chunkPaths: { type: 'array', items: { type: 'string' } },
  },
  required: ['applied', 'numNew', 'chunkPaths'],
}

const VET_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    outPath: { type: 'string' },
    flagged: { type: 'integer' },
  },
  required: ['outPath', 'flagged'],
}

function maintPrompt(round) {
  return `You maintain the build step of a Swedish wordlist vetting loop. Work in the wordlist repo directory (run \`cd ${DIR}\` first). Run the three commands EXACTLY as given; do not improvise. Then report the printed values.

STEP 1 — apply blocks that vetting agents wrote to vet/out_*.txt last round (idempotent), then remove those out-files. Run exactly:
python3 - <<'PYEOF'
import glob, os
seen = set()
if os.path.exists('vetted-block.txt'):
    for l in open('vetted-block.txt', encoding='utf-8'):
        if l.strip() and not l.startswith('#'):
            seen.add(l.split('\\t')[0])
n = 0
outs = sorted(glob.glob('vet/out_*.txt'))
with open('vetted-block.txt', 'a', encoding='utf-8') as f:
    for fn in outs:
        for l in open(fn, encoding='utf-8'):
            l = l.rstrip('\\n')
            if not l.strip():
                continue
            parts = l.split('\\t')
            w = parts[0].strip()
            cat = parts[1].strip() if len(parts) > 1 and parts[1].strip() else 'vetted'
            if w and w not in seen:
                f.write(w + '\\t' + cat + '\\n'); seen.add(w); n += 1
for fn in outs:
    os.remove(fn)
print('APPLIED', n)
PYEOF

STEP 2 — rebuild (must print "Prefix-code verified"):
python3 build_wordlist.py

STEP 3 — compute words not yet vetted and split into chunks of ${CHUNK}. Run exactly:
python3 - <<'PYEOF'
import os, json
cur = [l.strip() for l in open('sv-diceware-7776.plain.txt', encoding='utf-8') if l.strip()]
seen = set()
if os.path.exists('vetted-seen.txt'):
    seen = {l.strip() for l in open('vetted-seen.txt', encoding='utf-8') if l.strip()}
new = [w for w in cur if w not in seen]
os.makedirs('vet', exist_ok=True)
paths = []
for i in range(0, len(new), ${CHUNK}):
    p = f'vet/r${round}_c{i//${CHUNK}:03d}.txt'
    open(p, 'w', encoding='utf-8').write('\\n'.join(new[i:i+${CHUNK}]) + '\\n')
    paths.append(p)
with open('vetted-seen.txt', 'a', encoding='utf-8') as f:
    for w in new:
        f.write(w + '\\n')
print('NUMNEW', len(new))
print('PATHS', json.dumps(paths))
PYEOF

Report: applied (integer after APPLIED), numNew (integer after NUMNEW), chunkPaths (JSON array after PATHS).`
}

function vetPrompt(path) {
  const out = path.replace(/vet\/r/, 'vet/out_r')
  return `cd ${DIR}. Read the file ${path} — it lists Swedish base-form words (one per line), candidates for a Diceware passphrase wordlist used in a BankID-adjacent security app (Dagning, a Swedish housing-association board-management app).

Decide which words must be EXCLUDED. EXCLUDE a word if it is any of:
- svordom: profanity / swear / vulgar
- sexuellt: sexual, or explicit/sexual anatomy
- vald: violence, weapon, war, military, death, killing, self-harm
- medicinskt: disease, illness, injury, clinical or medical-distress term
- substans: alcohol, drug, narcotic, tobacco or other intoxicant (alkohol, akvavit, amfetamin, absint)
- religion: religion, faith, denomination, clergy, scripture, ritual
- nationalitet: nationality, language, ethnicity, or country/city/region/place name (afghan, afrikaans, albanska)
- egennamn: proper name — person, brand, company, organisation, mythological/biblical figure, or eponym (adonis, alzheimer)
- politik: politically charged or controversial topic (abort)
- negativt: strongly negative, unpleasant, fear, crime, contempt, distress
- ackel: disgust / bodily waste
- funktionsord: function or closed-class word — pronoun, preposition, conjunction, numeral, or pure adverb
- olamplig: awkward, archaic, very obscure, technical jargon, a fragment, an abbreviation, or otherwise not a normal memorable everyday Swedish word

KEEP everyday, concrete, neutral, memorable Swedish words: nature, animals, plants, food/drink (non-alcoholic), household objects, tools, clothing, common neutral verbs, neutral descriptive adjectives, weather, colours, ordinary professions (not military/clergy). Do NOT exclude a word merely for being an English loanword if it is well-established and neutral (cykel, jobb, mejl, video, projekt are fine).

This is security-sensitive — when a word is genuinely offensive, distressing, embarrassing, controversial, intoxicant-related, a proper name, or a nationality/place, EXCLUDE it. For ordinary neutral words, KEEP them.

Then WRITE your exclusions to the file ${out} (create it), one per line in the format:
word<TAB>category
Use the EXACT spelling from the input file (including å ä ö). Write nothing but those lines. If no word should be excluded, create ${out} as an empty file.

You can do the write with a single command, e.g.:
printf 'ord1\\tkategori\\nord2\\tkategori\\n' > ${out}

Return outPath="${out}" and flagged = the number of words you wrote.`
}

// ---- loop ----
let round = 0
let lastFlag = -1
while (round < MAX_ROUNDS) {
  round++
  const m = await agent(maintPrompt(round), {
    schema: MAINT_SCHEMA, label: `build r${round}`, phase: 'Build',
  })
  if (!m) { log(`round ${round}: build agent failed`); break }
  log(`round ${round}: applied ${m.applied} prior blocks, ${m.numNew} new words to vet`)
  if (m.numNew === 0) { log(`round ${round}: nothing new — converged`); break }
  const res = await parallel(m.chunkPaths.map((p, i) => () =>
    agent(vetPrompt(p), { schema: VET_SCHEMA, label: `vet r${round} c${i}`, phase: 'Vet' })
  ))
  lastFlag = res.filter(Boolean).reduce((a, r) => a + (r.flagged || 0), 0)
  log(`round ${round}: vetted ${m.numNew}, flagged ${lastFlag}`)
  if (lastFlag === 0) { log('no new flags — converged'); break }
}

// final apply of the last round's out-files (maintainer STEP 1 only)
const fin = await agent(`cd ${DIR}. Run STEP 1 only (apply vet/out_*.txt to vetted-block.txt and remove them), then rebuild once with python3 build_wordlist.py.

python3 - <<'PYEOF'
import glob, os
seen=set()
if os.path.exists('vetted-block.txt'):
    for l in open('vetted-block.txt',encoding='utf-8'):
        if l.strip() and not l.startswith('#'): seen.add(l.split('\\t')[0])
n=0; outs=sorted(glob.glob('vet/out_*.txt'))
with open('vetted-block.txt','a',encoding='utf-8') as f:
    for fn in outs:
        for l in open(fn,encoding='utf-8'):
            l=l.rstrip('\\n')
            if not l.strip(): continue
            p=l.split('\\t'); w=p[0].strip(); c=p[1].strip() if len(p)>1 and p[1].strip() else 'vetted'
            if w and w not in seen: f.write(w+'\\t'+c+'\\n'); seen.add(w); n+=1
for fn in outs: os.remove(fn)
print('APPLIED',n)
PYEOF
python3 build_wordlist.py

Report what "APPLIED" printed and whether the build printed "Prefix-code verified".`, { label: 'final apply', phase: 'Build' })

log(`final apply: ${fin}`)
return { rounds: round, lastRoundFlagged: lastFlag }
