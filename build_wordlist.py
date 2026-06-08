#!/usr/bin/env python3
"""
Build a curated Swedish Diceware wordlist (7776 = 6^5) from SALDO lemmas,
ranked by wordfreq (ranking signal only; not redistributed -> license derives
from SALDO (CC BY 3.0) alone; output published as CC BY 4.0).

Run:  python3 build_wordlist.py            # full run -> writes outputs
      python3 build_wordlist.py --explore  # stage diagnostics, no writes
      python3 build_wordlist.py --sweep    # zipf-floor survival sweep
"""
import sys
import re
import xml.etree.ElementTree as ET
from collections import Counter
from wordfreq import zipf_frequency
from blocklists import (STOPWORDS, PROFANITY, PROFANITY_CONTAINS,
                        PROFANITY_EXACT_EXTRA, NATIONALITY, RELIGION, NEGATIVE,
                        NEGATIVE_CONTAINS, WHITELIST, MILITARY, MEDICAL_EXTRA,
                        GENITIVE)

SALDO = "saldo.xml"
TARGET = 7776
# PREFIX_LEN = 0 -> prefix-free only (no fixed N-char distinguishability window).
# Chosen for an app-generated 4-word passphrase: entropy is in the selection, the
# N-char "type-to-disambiguate" convenience is irrelevant, but prefix-freeness
# still guarantees unambiguous decoding if words are concatenated w/o separators.
PREFIX_LEN = 0
KEEP_POS = {"nn", "av", "vb"}

MIN_LEN = 4
MAX_LEN = 9
ZIPF_FLOOR = 0.0          # include unattested as backstop so the loop can't crash;
                          # greedy still takes most-common-first, so attested win
ZIPF_CEIL = 6.6           # skip the very top function-word band

WORD_RE = re.compile(r"^[a-z]+$")   # plain a-z only — no å/ä/ö (easy typing)

MODE = "full"
if "--explore" in sys.argv:
    MODE = "explore"
elif "--sweep" in sys.argv:
    MODE = "sweep"


# ---------------------------------------------------------------------------
# 1. Parse SALDO: first FormRepresentation of each Lemma = canonical base form
# ---------------------------------------------------------------------------
def parse_saldo(path):
    pos_counts = Counter()
    n_entries = 0
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag != "LexicalEntry":
            continue
        n_entries += 1
        lemma = elem.find("Lemma")
        if lemma is not None:
            fr = lemma.find("FormRepresentation")
            if fr is not None:
                wf = pos = None
                for feat in fr.findall("feat"):
                    a = feat.get("att")
                    if a == "writtenForm":
                        wf = feat.get("val")
                    elif a == "partOfSpeech":
                        pos = feat.get("val")
                if wf is not None and pos is not None:
                    pos_counts[pos] += 1
                    yield wf, pos
        elem.clear()
    parse_saldo.n_entries = n_entries
    parse_saldo.pos_counts = pos_counts


# ---------------------------------------------------------------------------
# Pipeline stages -> returns (ranked_pool, stats)
#   ranked_pool: list of (word, zipf) sorted by zipf desc, after char/len/freq
#   also returns the raw content-lemma dict for stopword/profanity accounting
# ---------------------------------------------------------------------------
def build_ranked_pool(min_len, max_len, zipf_floor, zipf_ceil):
    raw = {}
    for wf, pos in parse_saldo(SALDO):
        if pos in KEEP_POS:
            raw.setdefault(wf, set()).add(pos)

    stats = {
        "lexical_entries": parse_saldo.n_entries,
        "content_pos_lemmas_raw": len(raw),
    }

    charok = {}
    rej_char = rej_len = 0
    for w, pset in raw.items():
        if not WORD_RE.match(w):
            rej_char += 1
            continue
        if not (min_len <= len(w) <= max_len):
            rej_len += 1
            continue
        charok[w] = pset
    stats["rejected_nonword_chars"] = rej_char
    stats["rejected_length"] = rej_len
    stats["after_char_len_filter"] = len(charok)

    scored = []
    n_zero = n_low = n_high = 0
    for w in charok:
        z = zipf_frequency(w, "sv")
        if z == 0.0 and zipf_floor > 0.0:
            n_zero += 1
        elif z < zipf_floor:
            n_low += 1
        elif z > zipf_ceil:
            n_high += 1
        else:
            scored.append((w, z))
    scored.sort(key=lambda t: (-t[1], t[0]))
    stats["dropped_zipf_zero"] = n_zero
    stats["dropped_below_floor"] = n_low
    stats["dropped_above_ceil"] = n_high
    stats["freq_ranked_pool"] = len(scored)
    return scored, stats


# ---------------------------------------------------------------------------
# 5/6. Stopword + profanity filters, then greedy prefix-code selection
# ---------------------------------------------------------------------------
def load_vetted(path="vetted-block.txt"):
    """Dynamic blocklist appended by the agent-vetting loop. Lines: word<TAB>category."""
    d = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                w = parts[0].strip()
                cat = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "vetted"
                if w:
                    d[w] = cat
    except FileNotFoundError:
        pass
    return d


VETTED = load_vetted()


def filter_blocklists(scored):
    """Return (survivors, flagged) where flagged = [(word, category, reason)]."""
    survivors = []
    flagged = []
    for w, z in scored:
        if w in VETTED:
            flagged.append((w, VETTED[w], "agent-vetted"))
            continue
        if w in STOPWORDS:
            flagged.append((w, "function_word", "closed-class/grammatical"))
            continue
        if w in NATIONALITY:
            flagged.append((w, "nationalitet", "place/region/demonym"))
            continue
        if w in RELIGION:
            flagged.append((w, "religion", "religious vocabulary"))
            continue
        if w in NEGATIVE:
            flagged.append((w, "negativt", "negative connotation"))
            continue
        if w in MILITARY:
            flagged.append((w, "vald", "military/war"))
            continue
        if w in MEDICAL_EXTRA:
            flagged.append((w, "medicinskt", "medical-distress"))
            continue
        if w in GENITIVE:
            flagged.append((w, "genitivform", "reads as genitive"))
            continue
        if w in PROFANITY:
            flagged.append((w, PROFANITY[w], "exact-match"))
            continue
        if w in PROFANITY_EXACT_EXTRA:
            flagged.append((w, PROFANITY_EXACT_EXTRA[w], "exact-compound"))
            continue
        if w in WHITELIST:
            survivors.append((w, z))
            continue
        hit = next((stem for stem in PROFANITY_CONTAINS if stem in w), None)
        if hit:
            flagged.append((w, PROFANITY_CONTAINS[hit], f"contains '{hit}'"))
            continue
        nhit = next((stem for stem in NEGATIVE_CONTAINS if stem in w), None)
        if nhit:
            flagged.append((w, NEGATIVE_CONTAINS[nhit], f"contains '{nhit}'"))
            continue
        survivors.append((w, z))
    return survivors, flagged


def greedy_prefix_select(survivors, target, prefix_len):
    """Greedy by descending freq; enforce a prefix code.

    prefix_len > 0 also enforces first-N-char distinguishability; prefix_len == 0
    means prefix-free only. Rejects a candidate if:
      - (prefix_len>0) its first `prefix_len` chars collide with a kept word's, OR
      - it is a prefix of a kept word, OR a kept word is a prefix of it.
    Returns (kept_words, dropped_for_prefix_count).
    """
    kept = []
    taken_trunc = set()       # first prefix_len chars of kept words
    kept_set = set()          # full kept words
    kept_prefix_set = set()   # every prefix of every kept word
    dropped = 0
    for w, z in survivors:
        trunc = w[:prefix_len] if prefix_len else None
        if prefix_len and trunc in taken_trunc:
            dropped += 1
            continue
        # a kept word is a prefix of w?
        if any(w[:i] in kept_set for i in range(1, len(w))):
            dropped += 1
            continue
        # w is a prefix of a kept word?
        if w in kept_prefix_set:
            dropped += 1
            continue
        kept.append((w, z))
        if prefix_len:
            taken_trunc.add(trunc)
        kept_set.add(w)
        for i in range(1, len(w) + 1):
            kept_prefix_set.add(w[:i])
        if len(kept) >= target:
            break
    return kept, dropped


# ---------------------------------------------------------------------------
# Verification: assert the final list is a valid prefix code
# ---------------------------------------------------------------------------
def verify_prefix_code(words, prefix_len):
    assert len(words) == len(set(words)), "duplicates present"
    if prefix_len:
        truncs = [w[:prefix_len] for w in words]
        assert len(truncs) == len(set(truncs)), "first-%d-char collision" % prefix_len
    s = sorted(words)
    for a, b in zip(s, s[1:]):
        assert not b.startswith(a), f"'{a}' is a prefix of '{b}'"
    return True


def to_dice(idx):
    """0..7775 -> five base-6 dice digits string like '11111'."""
    digits = []
    for _ in range(5):
        digits.append(str(idx % 6 + 1))
        idx //= 6
    return "".join(reversed(digits))


# ---------------------------------------------------------------------------
def main():
    if MODE == "sweep":
        print("zipf-floor survival sweep (band %d-%d, prefix=%d):"
              % (MIN_LEN, MAX_LEN, PREFIX_LEN))
        for floor in [3.0, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5]:
            scored, st = build_ranked_pool(MIN_LEN, MAX_LEN, floor, ZIPF_CEIL)
            surv, flagged = filter_blocklists(scored)
            kept, dropped = greedy_prefix_select(surv, TARGET, PREFIX_LEN)
            min_z = kept[-1][1] if kept else 0
            print(f"  floor {floor:>4}: pool={len(scored):5d} "
                  f"after_block={len(surv):5d} flagged={len(flagged):4d} "
                  f"kept={len(kept):5d} prefix_dropped={dropped:5d} "
                  f"min_zipf_kept={min_z:.2f}")
        return

    scored, stats = build_ranked_pool(MIN_LEN, MAX_LEN, ZIPF_FLOOR, ZIPF_CEIL)

    if MODE == "explore":
        for k, v in stats.items():
            print(f"  {k:28s} {v}")
        surv, flagged = filter_blocklists(scored)
        kept, dropped = greedy_prefix_select(surv, TARGET, PREFIX_LEN)
        print(f"  after_blocklists           {len(surv)}")
        print(f"  flagged_total              {len(flagged)}")
        print(f"  prefix_dropped             {dropped}")
        print(f"  final_kept                 {len(kept)}")
        return

    # ---- full run ----
    surv, flagged = filter_blocklists(scored)
    kept, dropped = greedy_prefix_select(surv, TARGET, PREFIX_LEN)

    if len(kept) < TARGET:
        print(f"ERROR: only {len(kept)} survived (< {TARGET}). "
              f"Loosen band/floor in constants and re-run.", file=sys.stderr)
        sys.exit(1)

    words = sorted(w for w, _ in kept[:TARGET])
    verify_prefix_code(words, PREFIX_LEN)

    # outputs --------------------------------------------------------------
    with open("sv-diceware-7776.txt", "w", encoding="utf-8") as f:
        for i, w in enumerate(words):
            f.write(f"{to_dice(i)}\t{w}\n")
    with open("sv-diceware-7776.plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(words) + "\n")
    with open("flagged.txt", "w", encoding="utf-8") as f:
        f.write("# Removed by stopword + profanity/connotation pass.\n")
        f.write("# Format: word <TAB> category <TAB> reason\n")
        f.write("# REVIEW NEEDED — native-speaker eyes; not assumed complete.\n\n")
        for w, cat, reason in sorted(flagged):
            f.write(f"{w}\t{cat}\t{reason}\n")

    write_stats(stats, scored, surv, flagged, kept, words, dropped)
    write_license_note()

    # acceptance: 20-word random-ish sample (deterministic stride, no RNG)
    print(f"OK: wrote {len(words)} words. Prefix-code verified.")
    print(f"mean length = {sum(len(w) for w in words)/len(words):.2f}")
    stride = len(words) // 20
    print("\n20-word sample:")
    for i in range(20):
        w = words[i * stride]
        print(f"  {to_dice(i*stride)}  {w}")


def write_stats(stats, scored, surv, flagged, kept, words, dropped):
    lh = Counter(len(w) for w in words)
    catc = Counter(c for _, c, _ in flagged)
    mean_len = sum(len(w) for w in words) / len(words)
    with open("STATS.md", "w", encoding="utf-8") as f:
        f.write("# Swedish Diceware 7776 — build statistics\n\n")
        f.write(f"- Length band used: **{MIN_LEN}–{MAX_LEN}** characters "
                f"(lowercase **a–z only**, no å/ä/ö)\n")
        f.write(f"- zipf floor / ceiling: **{ZIPF_FLOOR} / {ZIPF_CEIL}** "
                f"(wordfreq 'sv', ranking signal only)\n")
        prefdesc = (f"first **{PREFIX_LEN}** characters + prefix-free"
                    if PREFIX_LEN else "**prefix-free only** (no word is a prefix "
                    "of another; N-char window dropped — see notes)")
        f.write(f"- Prefix property: {prefdesc}\n\n")
        f.write("## Pipeline funnel\n\n")
        f.write(f"| Stage | Count |\n|---|---|\n")
        f.write(f"| SALDO LexicalEntry elements | {stats['lexical_entries']} |\n")
        f.write(f"| Content-POS lemmas (nn/av/vb, deduped) | {stats['content_pos_lemmas_raw']} |\n")
        f.write(f"| Rejected: non a–zåäö chars (caps/hyphen/digit) | {stats['rejected_nonword_chars']} |\n")
        f.write(f"| Rejected: outside length band | {stats['rejected_length']} |\n")
        f.write(f"| After char + length filter | {stats['after_char_len_filter']} |\n")
        f.write(f"| Dropped: zipf == 0 (unattested) | {stats['dropped_zipf_zero']} |\n")
        f.write(f"| Dropped: below zipf floor | {stats['dropped_below_floor']} |\n")
        f.write(f"| Dropped: above zipf ceiling | {stats['dropped_above_ceil']} |\n")
        f.write(f"| Frequency-ranked pool | {stats['freq_ranked_pool']} |\n")
        f.write(f"| Removed by stopword + profanity pass | {len(flagged)} |\n")
        f.write(f"| After blocklists | {len(surv)} |\n")
        f.write(f"| Dropped by prefix-code selection | {dropped} |\n")
        f.write(f"| **Final selected** | **{len(words)}** |\n\n")
        f.write("## Flagged breakdown by category\n\n")
        f.write("| Category | Count |\n|---|---|\n")
        for c, n in catc.most_common():
            f.write(f"| {c} | {n} |\n")
        f.write(f"\n## Length distribution (final)\n\n")
        f.write("| Length | Count |\n|---|---|\n")
        for L in sorted(lh):
            f.write(f"| {L} | {lh[L]} |\n")
        f.write(f"\n- Mean word length: **{mean_len:.2f}**\n")
        f.write(f"- Min zipf among selected: **{kept[-1][1]:.2f}** "
                f"(rarest kept word: '{kept[-1][0]}')\n")
        f.write(f"- Entropy: log2(7776) = **12.925 bits/word**; "
                f"4 words = **51.70 bits**\n")
        f.write(f"- Prefix-uniqueness check: **PASSED** "
                f"(verified programmatically in build_wordlist.py)\n")


def write_license_note():
    with open("LICENSE-NOTE.md", "w", encoding="utf-8") as f:
        f.write("""# License & attribution — sv-diceware-7776

## Wordlist data files
`sv-diceware-7776.txt` and `sv-diceware-7776.plain.txt` are a curated derivative
of the **SALDO** morphological lexicon.

- **Source:** SALDO, Språkbanken Text, University of Gothenburg.
- **Source license:** Creative Commons Attribution (**CC BY 3.0**) — attribution
  only, **no ShareAlike / no copyleft**.
- Because CC BY imposes no ShareAlike obligation, this derivative may be released
  under any license that preserves the required attribution. It is published
  under **CC BY 4.0**.

### Attribution
> Swedish Diceware Wordlist © 2026 Marcin Wolniewicz, licensed CC BY 4.0.
> Contains lemmas derived from SALDO (Språkbanken Text, University of
> Gothenburg), licensed CC BY 3.0. The selection and curation of this
> 7776-word Diceware list is the work of Marcin Wolniewicz.

## Ranking signal — wordfreq (NOT in the license chain)
The Python package **wordfreq** (MIT) was used only as a *ranking signal* to
order SALDO lemmas by commonness during selection. No wordfreq data is copied
into or redistributed with the output. The words themselves all originate from
SALDO. Therefore wordfreq does **not** enter the license chain and imposes no
obligations on the published wordlist.

## Code license (MIT)
The **code** in this repository — `build_wordlist.py`, `blocklists.py`,
`vet_workflow.js`, and `gen_passphrase.py` — is © 2026 Marcin Wolniewicz and
published under the **MIT License** (see `LICENSE-MIT`).

## Scope
- **Wordlist data files** (`sv-diceware-7776.txt`, `sv-diceware-7776.plain.txt`,
  and the derived reports): **CC BY 4.0** (see above).
- **Code** in this repository: **MIT** (see above).
""")


if __name__ == "__main__":
    main()
