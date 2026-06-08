#!/usr/bin/env python3
"""
Generate Diceware passphrases from the curated Swedish wordlist.

Selection is uniform and independent per word (repetitions allowed), using a
cryptographically secure RNG (secrets) — the same approach the app must use.

Usage:
  python3 gen_passphrase.py                 # 15 phrases of 4 words
  python3 gen_passphrase.py -w 4 -n 20      # 20 phrases of 4 words
  python3 gen_passphrase.py --dice          # also show the 5-digit dice codes
"""
import argparse
import math
import secrets

LIST = "sv-diceware-7776.plain.txt"


def load_words(path=LIST):
    words = [w.strip() for w in open(path, encoding="utf-8") if w.strip()]
    if len(words) != 7776:
        raise SystemExit(f"expected 7776 words, got {len(words)} in {path}")
    return words


def to_dice(idx):
    digits = []
    for _ in range(5):
        digits.append(str(idx % 6 + 1))
        idx //= 6
    return "".join(reversed(digits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--words", type=int, default=4, help="words per phrase")
    ap.add_argument("-n", "--num", type=int, default=15, help="number of phrases")
    ap.add_argument("--dice", action="store_true", help="show dice codes too")
    args = ap.parse_args()

    words = load_words()
    bits = args.words * math.log2(len(words))
    print(f"wordlist: {len(words)} words  |  {math.log2(len(words)):.3f} bits/word")
    print(f"phrase:   {args.words} words  ≈  {bits:.1f} bits of entropy\n")

    for _ in range(args.num):
        idxs = [secrets.randbelow(len(words)) for _ in range(args.words)]
        phrase = " ".join(words[i] for i in idxs)
        if args.dice:
            codes = " ".join(to_dice(i) for i in idxs)
            print(f"  {phrase:<44}  [{codes}]")
        else:
            print(f"  {phrase}")


if __name__ == "__main__":
    main()
