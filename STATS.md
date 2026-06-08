# Swedish Diceware 7776 — build statistics

- Length band used: **4–9** characters (lowercase **a–z only**, no å/ä/ö)
- zipf floor / ceiling: **0.0 / 6.6** (wordfreq 'sv', ranking signal only)
- Prefix property: **prefix-free only** (no word is a prefix of another; N-char window dropped — see notes)

## Pipeline funnel

| Stage | Count |
|---|---|
| SALDO LexicalEntry elements | 131020 |
| Content-POS lemmas (nn/av/vb, deduped) | 106252 |
| Rejected: non a–zåäö chars (caps/hyphen/digit) | 38402 |
| Rejected: outside length band | 35393 |
| After char + length filter | 32457 |
| Dropped: zipf == 0 (unattested) | 0 |
| Dropped: below zipf floor | 0 |
| Dropped: above zipf ceiling | 0 |
| Frequency-ranked pool | 32457 |
| Removed by stopword + profanity pass | 6630 |
| After blocklists | 25827 |
| Dropped by prefix-code selection | 4927 |
| **Final selected** | **7776** |

## Flagged breakdown by category

| Category | Count |
|---|---|
| olamplig | 2534 |
| negativt | 1000 |
| vald | 586 |
| nationalitet | 505 |
| medicinskt | 492 |
| religion | 347 |
| sexuellt | 234 |
| egennamn | 227 |
| substans | 179 |
| user-flagged | 170 |
| politik | 121 |
| äckel | 95 |
| function_word | 81 |
| svordom | 33 |
| slur | 8 |
| spel | 8 |
| ackel | 5 |
| nedsättande | 4 |
| genitivform | 1 |

## Length distribution (final)

| Length | Count |
|---|---|
| 4 | 805 |
| 5 | 1292 |
| 6 | 1537 |
| 7 | 1533 |
| 8 | 1430 |
| 9 | 1179 |

- Mean word length: **6.65**
- Min zipf among selected: **1.16** (rarest kept word: 'tamtam')
- Entropy: log2(7776) = **12.925 bits/word**; 4 words = **51.70 bits**
- Prefix-uniqueness check: **PASSED** (verified programmatically in build_wordlist.py)
