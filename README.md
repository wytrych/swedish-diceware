# Swedish Diceware Wordlist (7776 words)

A curated Swedish word list of exactly **7,776 words** (6⁵) for generating
Diceware-style passphrases. Each word maps to a five-digit base-6 code
(`11111`–`66666`), so five dice rolls — or 12.925 bits of entropy from a CSPRNG —
select one word. A four-word passphrase carries **log₂(7776⁴) ≈ 51.7 bits**.

The wordlist data is licensed under **CC BY 4.0**; the code in this repo under **MIT**.

**This is a subjective list so please submit PRs to help improve it and remove any
potential risky or inappropriate words, or to add any suitable words.
See [Limitations](#limitations).**

## Properties of the final list

| Property | Value |
|---|---|
| Word count | exactly 7,776 (6⁵) |
| Character set | lowercase **a–z only** (no å/ä/ö) |
| Word length | 4–9 characters |
| Forms | base forms only (noun singular indefinite, verb infinitive, adjective uninflected) |
| Numbering | `11111`–`66666` (five base-6 "dice" digits), in sorted order |
| Prefix property | **prefix-free** — no word is a prefix of another |
| Frequency | every word is corpus-attested; rarest zipf 1.16, median 2.75 |
| Mean length | 6.65 characters |
| Entropy | 12.925 bits/word; 4 words ≈ 51.7 bits |

**Why a–z only:** removing å/ä/ö makes passphrases easy to type on any keyboard
layout, at the cost of a smaller candidate pool (handled below).

**Why prefix-free instead of the EFF "first-5-characters-unique" rule:** for an
*app-generated* passphrase the user never types a word into an autocomplete box,
so the 5-char "type-to-disambiguate" convenience buys nothing. The property that
*does* matter — that a passphrase concatenated without separators decodes
unambiguously — is guaranteed by prefix-freeness alone. Dropping the fixed
5-char window also lets the list keep the most common, most memorable words.
(See [Decisions](#design-decisions) for the data behind this.)

## Background: the EFF Diceware lists

[Diceware](https://en.wikipedia.org/wiki/Diceware) is a method for generating
passphrases by mapping dice rolls to words in a numbered list. In 2016 the
**[Electronic Frontier Foundation](https://www.eff.org/dice)** (EFF) — a US digital
-rights non-profit — published a modern, curated set of Diceware wordlists
(designed by cryptographer Joseph Bonneau) that have become the de-facto
standard. There are three:

- **Long list** — **7,776 words** (6⁵, five dice per word, ~12.9 bits/word),
  curated for recognizable, easy-to-spell words with no profanity. **This list
  mirrors the EFF long list's format.**
- **Short list #1** — 1,296 short words (four dice).
- **Short list #2** — 1,296 words, *autocomplete-optimized*: each word is
  uniquely identified by its **first three characters**, and words differ by
  several edits to reduce typos.

When this document refers to the **"EFF prefix property"** or the
**"first-N-characters-unique rule,"** it means that short-list #2 design idea —
*not* a formal coding-theory term. The original spec for this project adapted it
to "distinguishable within the first 5 characters." As the
[Decisions](#design-decisions) section explains, that strict variant proved too
costly for an a–z-only Swedish list, so we kept the part that actually protects
entropy under separator-less concatenation (**prefix-freeness**) and dropped the
fixed N-character window.

## Files

| File | Description |
|---|---|
| `sv-diceware-7776.txt` | Final list, `11111\tword` per line (tab-separated) |
| `sv-diceware-7776.plain.txt` | Final list, one word per line |
| `STATS.md` | Pipeline funnel, length distribution, prefix check |
| `LICENSE-NOTE.md` | License chain and attribution |
| `flagged.txt` | Every removed word, with category and reason |
| `vetted-block.txt` | Cumulative blocklist consumed by the build (word + category) |
| `review-candidates.txt` | Kept words matching sensitive stems, for a final human skim |
| `build_wordlist.py` | The reproducible build pipeline |
| `blocklists.py` | Static Swedish blocklists (function words, profanity, etc.) |
| `vet_workflow.js` | The multi-agent vetting loop (see below) |
| `gen_passphrase.py` | Generate example passphrases from the list (see [Generating passphrases](#generating-passphrases)) |

The source lexicon `saldo.xml` (~74 MB) is **not** redistributed here — download
it from Språkbanken (link below).

## Sources

- **Word data: [SALDO](https://spraakbanken.gu.se/resurser/saldo)** — a
  morphological lexicon of Swedish from Språkbanken Text, University of
  Gothenburg. We use it as the **base-form source**: it is a lemma lexicon, so
  by extracting lemmas we avoid inflected/conjugated tokens by construction.
  Licensed **[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)**
  (attribution only — no ShareAlike).
- **Frequency ranking: [`wordfreq`](https://pypi.org/project/wordfreq/)** (MIT) —
  used **only as a ranking signal** to order SALDO lemmas by commonness. No
  wordfreq data is copied into the output, so it is **not** part of the license
  chain. See `LICENSE-NOTE.md`.

## License

This repo is **dual-licensed**:

- **Wordlist data** (`sv-diceware-7776.txt`, `sv-diceware-7776.plain.txt`, and
  the derived reports) — **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**
  (`LICENSE`). It is a derivative of SALDO, which is licensed
  **[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)** (attribution
  only, no ShareAlike/copyleft), so we are free to choose the derivative's
  license; attribution to Språkbanken/SALDO is required.
- **Code** (`build_wordlist.py`, `blocklists.py`, `vet_workflow.js`,
  `gen_passphrase.py`) — **[MIT](https://opensource.org/license/mit)**
  (`LICENSE-MIT`).

Full details and attribution text in `LICENSE-NOTE.md`.

---

## The pipeline

The build (`build_wordlist.py`) is deterministic and reproducible. Given
`saldo.xml` and the blocklists, it always produces the same 7,776 words.

### 1. Parse SALDO, extract lemmas
Stream the LMF XML and, for each `<LexicalEntry>`, take the first
`<FormRepresentation>` of its `<Lemma>` — the canonical base form — together
with its part of speech.

### 2. Keep only content parts of speech
Keep nouns (`nn`), adjectives (`av`), and verbs (`vb`). Everything else is
dropped: proper names (`pm`), multiword expressions (`*m`), abbreviations
(`*a`), affixes/compound-only forms (`*h`, `*xc`), and closed-class words
(`ab`, `pp`, `pn`, `kn`, `nl`, `in`, `sn`). Deduplicate by surface form.

### 3. Character & length filter
Keep words matching `^[a-z]{4,9}$` — lowercase a–z only, 4–9 characters.
Uppercase, hyphens, digits, and å/ä/ö are all rejected here. (Rejecting
uppercase also discards lowercased proper-noun homographs.)

### 4. Frequency ranking
Score each surviving lemma with `zipf_frequency(word, "sv")` from `wordfreq`
and sort descending. The frequency is a *ranking signal only* — selection
always prefers the most common words first.

### 5. Static blocklists
Remove function words and obviously unsuitable terms via curated Swedish
blocklists (`blocklists.py`): closed-class/grammatical homographs (e.g.
`skulle` "hayloft" reads as the modal "would"), profanity, sexual and
anatomical terms, violence/weapons, medical-distress, disgust, slurs,
nationalities/languages, religion, and strongly negative-connotation words.

### 6. Greedy prefix-free selection
Walk the frequency-ranked survivors from most to least common, keeping a word
only if it is **not** a prefix of any already-kept word and **no** kept word is
a prefix of it. Stop at 7,776. Because we process in frequency order, when two
words conflict the more common one wins.

### 7. Number and emit
Sort the 7,776 words and assign codes `11111`–`66666` by converting each index
to five base-6 digits. The build **asserts** the prefix-free property and that
the result is exactly 7,776 unique a–z words before writing output.

### Funnel

| Stage | Count |
|---|---|
| SALDO `LexicalEntry` elements | 131,020 |
| Content-POS lemmas (nn/av/vb, deduped) | 106,252 |
| After character + length filter (a–z, 4–9) | 32,457 |
| Removed by blocklists (static + vetting + human) | 6,630 |
| After blocklists | 25,827 |
| Dropped by prefix-free selection | 4,927 |
| **Final** | **7,776** |

---

## Quality control: a three-layer filter

Word *suitability* (vs. mere grammatical correctness) cannot be decided by
frequency or part of speech alone. We used three layers, in order of increasing
human involvement:

### Layer 1 — Static blocklists (`blocklists.py`)
LLM-written Swedish lists for the unambiguous cases: function words, swear
words, sexual/violent/medical terms, nationalities, religion, etc. These are
applied on every build.

### Layer 2 — Multi-agent vetting loop (`vet_workflow.js`)
Blocklists can't anticipate every unsuitable word in a 30,000-word pool
(intoxicants like *akvavit*, mythological names like
*adonis*, controversial topics, obscure jargon, …). So every
candidate word was reviewed by an LLM agent against an explicit rubric:
**svordom** (profanity), **sexuellt**, **våld** (violence/weapons/military),
**medicinskt** (disease/distress), **substans** (alcohol/drugs/tobacco),
**religion**, **nationalitet**, **egennamn** (proper names/brands/eponyms),
**politik** (controversial), **negativt**, **äckel** (disgust),
**funktionsord**, and **olämplig** (awkward/obscure/jargon). Everyday concrete
words (nature, animals, food, tools, neutral verbs/adjectives) are kept;
well-established neutral loanwords are not removed merely for being loanwords.

The loop is a *generate → vet → block → regenerate* cycle that runs until it
converges:

1. Build the list and split the not-yet-vetted words into chunks (~150 each).
2. Fan out one agent per chunk, in parallel; each writes the words it judges
   unsuitable (with a category) to a file.
3. Append those to `vetted-block.txt` and rebuild. Removing words pulls new
   "backfill" words up from below the cutoff.
4. Re-vet only the backfill (a record of already-vetted words prevents
   re-checking). Repeat until a round flags nothing.

Because each removal is logged with its category and the seen-set is persisted,
the whole process is auditable in `flagged.txt` and resumable.

### Layer 3 — Human in the loop review (iterative)
A Swedish speaker, with the help of a separate LLM agent,
reviewed the converged list and flagged additional
words in batches — mild cases the agents had kept (e.g. slang rods
intoxicant terms, hard-to-spell loanwords like `gouache`/`zucchini`,
gambling/wine clusters).  Each batch was removed, the list rebuilt, and
the **backfill re-vetted by the agent loop** — so newly surfaced words
never enter unvetted. Where a flagged word had an inflection family
(e.g. `dyrka` → `dyrkan`/`dyrkare`/`dyrkande`, `spruta` → `sprut`/`sprutande`),
the whole family was blocked together.

### What was removed

6,630 words were removed in total. By category:

| Category | Count | | Category | Count |
|---|---|---|---|---|
| olämplig (awkward/obscure/jargon) | 2,534 | | egennamn (names/brands/eponyms) | 227 |
| negativt | 1,000 | | substans (alcohol/drugs/tobacco) | 179 |
| våld (violence/weapons/military) | 586 | | politik (controversial) | 121 |
| nationalitet (incl. languages) | 505 | | äckel (disgust) | 100 |
| medicinskt | 492 | | funktionsord | 81 |
| religion | 347 | | svordom + slur + nedsättande | 45 |
| sexuellt | 234 | | spel (gambling) + genitiv | 9 |

(~170 entries are tagged `user-flagged` for the human batches not assigned a
finer category.) The full list with per-word reasons is in `flagged.txt`.

---

## Design decisions

A few non-obvious choices and the data behind them.

**a–z only shrinks the pool a lot.** Of ~106k content lemmas, only 32,457 are
4–9-character a–z words. After all filtering, the strict EFF "first-5-chars
unique" rule left only ~7,464 quality words — *below* the 7,776 target. We
measured the keepable count under several prefix policies:

| Prefix policy | Keepable (quality words) |
|---|---|
| 4-char unique | ~6,255 |
| 5-char unique (EFF) | ~7,464 (short!) |
| 6-char unique | ~8,720 |
| prefix-free only | ~9,230 |

A *smaller* window is *stricter* (more collisions, fewer words), so 4-char is
worse, not better. We chose **prefix-free** — it reaches 7,776 with the most
common words and preserves the only security-relevant property (unambiguous
concatenation), while the dropped 5-char window was only ever a typing nicety
irrelevant to an app-generated passphrase.

**Frequency floor as a safety net.** Selection takes the most common words
first; the floor is set to 0 (include all attested words) purely so aggressive
removal during vetting can never starve the build below 7,776. In the final
list every word is attested (zipf ≥ 1.16) — the floor never had to reach for
obscure filler.

---

## Reproducing the build

Requirements: Python 3, `pip install wordfreq`, and `saldo.xml` from
Språkbanken in this directory.

```bash
pip install wordfreq
# place saldo.xml here
python3 build_wordlist.py            # writes the list + STATS.md + flagged.txt
python3 build_wordlist.py --explore  # stage-by-stage counts, no output files
python3 build_wordlist.py --sweep    # frequency-floor sensitivity sweep
```

The build consumes `blocklists.py` and `vetted-block.txt` (the accumulated
removals from vetting + human review) and re-asserts every invariant
(count = 7,776, a–z only, prefix-free, valid base-6 numbering) before writing.
Same inputs → identical output.

The agent vetting loop (`vet_workflow.js`) is provided for transparency; it
requires an agent runtime and is not needed to *reproduce* the list — its output
is already baked into `vetted-block.txt`.

## Generating passphrases

`gen_passphrase.py` produces example passphrases from the list. Word selection
is **uniform and independent per word, with repetitions allowed**, using Python's
`secrets` module — a cryptographically secure RNG, the same approach an
application must use (never `random`).

```bash
python3 gen_passphrase.py                 # 15 phrases of 4 words
python3 gen_passphrase.py -w 4 -n 20      # 20 phrases of 4 words
python3 gen_passphrase.py --dice          # also print the 5-digit dice codes
```

Example output:

```
wordlist: 7776 words  |  12.925 bits/word
phrase:   4 words  ≈  51.7 bits of entropy

  rubrik repstege orange motlut
  logisk silhuett stabil senig
  monogram konferens delikat trottoar
  center jippo gammal variabel
  hetluft ytlig knapp hemstad
```

With `--dice`, each word is shown with its five-digit base-6 code:

```
  spole influensa socka syrsa     [56312 26562 55454 61441]
  byggsats ormrot omljud opportun [15263 44315 43643 44162]
```

## Limitations

- The suitability judgment is inherently subjective. `flagged.txt` records every
  removal so the calls can be audited or reversed; `review-candidates.txt` lists
  kept words that match sensitive stems for a further human pass.
- The agent vetting is thorough but not infallible. Native-speaker review caught
  cases the agents kept; further review may surface more.
- "Awkward/obscure" (olämplig) is the largest and softest category. Erring
  toward removal is deliberate for a security/passphrase context, but it means
  some defensible words were dropped.

## Used by

This was built for [Dagning](https://dagning.app) (a Swedish housing-association
board-management app) to back app-generated passphrases, where word quality and
clean licensing matter. It is published here for transparency and reuse. Using it
yourself? Open a PR to include a link.
