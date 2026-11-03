"""price_rp9.py -- price moving secondary results to the note (caveat-study R-P9), on top of the cut list's 20 moves.

usage: python3 -I price_rp9.py [OUT.json] [--self-test]

Starting point: the paper at 58fa0b89 after the 20 moves of cutlist.json (44 distinct caveats, 7,484 blinded words).
Each candidate below removes the distinct caveats that would leave the paper with it, and the blinded words of what
moves. Words are TeX-section estimates calibrated to the blinded count (factor 1.062, the ratio of the blinded 8,080
to the TeX estimate of 7,610), less the words the 20 moves already saved in that section, plus or minus the edits named.
A caveat counts as removed only if every one of its statements left with the candidates chosen (the caveat's statement
sections are in cutlist.json). Abstract statements never leave: the abstract is protected text.

Search: every subset of the candidates that respects their dependencies; report those reaching <= 4.5 distinct per
1,000 words with the fewest candidates, and the best density reachable without any candidate a referee would expect a
PRD measurement paper to keep (`keep`).
"""
import itertools
import json
import sys
from pathlib import Path

BASE = {"distinct": 44, "words": 7484}
TARGET = 4.5

# key: (caveats removed, words removed, requires, keep, what the paper loses, cited by, note holds it)
CANDIDATES = {
    "IVC": (["C34", "C35", "C36", "C38"], 455, [], False,
            "IV C, the 2D covariance's construction and budget (blocks, the flux block smaller than the published one, "
            "the omitted terms); a one-sentence summary and a pointer stay",
            "VI A's coverage statement names the 2D covariance (it stays, pointing to the note)",
            "yes: note Sec. 4 (fuller, with its uncertainty and correlation figures)"),
    "IVB": (["C32", "C33", "C69"], 306, ["IVC"], True,
            "IV B, the 2D benchmark against the published result, and Fig. 1",
            "the abstract (\"reproduces the published muon-kinematic cross-section integral within about 1%\") and "
            "Sec. I (\"an end-to-end test of the unfolding\"): both would need editing, and the abstract is protected",
            "content yes: note Sec. 6, with its own comparison figures; Fig. 1 itself is not in the note"),
    "VC": (["MV03", "C11"], 108, [], False,
           "V C, the descriptive comparisons of the three- and four-observable central values, and the scope "
           "sentence on prediction definitions outside the sixteen cells (Sec. II)",
           "Sec. I (\"we also give three- and four-observable central values\")",
           "yes: note Secs. 7 and 8"),
    "IIIA": (["MV04"], 163, [], False,
             "III A, the reporting definitions, the precision target and the envelope",
             "the conclusions (the envelope as the second validation finding)",
             "yes: note Sec. 9.4"),
    "IVE": ([], 465, [], True,
            "IV E, the generator-sized truth changes, and Fig. 3 (regularization bias up to 74% at high W)",
            "the conclusions (the first validation finding, and the lessons paragraph)",
            "content yes: note Sec. 9, with its own figures; Fig. 3 itself is not in the note"),
    "IVE+IIIA:C20": (["C20"], 45, ["IVE", "IIIA"], True,
                     "the conclusions' two sentences on prior retention (C20 then leaves the paper)",
                     "the conclusions themselves", "yes: note Sec. 9"),
    "IVE+VC:C41": (["C41"], 25, ["IVE", "VC"], False,
                   "IV D's pointer to the earlier purity-subtracted result's normalization checks (C41 then leaves)",
                   "none", "yes: note Sec. 8.1"),
    "C65": (["C65"], 35, [], False, "VI A item 2, the four low-stability cells",
            "none", "yes: note register n58"),
    "MV10": (["MV10"], 80, [], True, "V B's χ² sensitivity to the assumed correlations",
             "none; it qualifies the χ² of Table III", "yes: note register n67"),
    "C30C31": (["C30", "C31"], 30, [], False, "IV A's zero training-seed block and the absent finite-ensemble correction",
               "none", "C31 yes (note register n61); C30 NOTE FIRST (not confirmed in the note)"),
    "C17": (["C17"], 0, [], False, "nothing: the iteration choice reworded as a plain choice with its basis (R-P4)",
            "none", "not a move; a coder may still count it"),
    "C76": (["C76"], 10, [], True, "Fig. 4's caption: the predictions' finite-sample uncertainties are not drawn",
            "none; it qualifies the figure of the main comparison", "no"),
    "MV07": (["MV07"], 70, [], True, "Table III's footnote on the hydrogen samples' defects",
             "none; it qualifies the compared predictions", "yes: note Sec. 10.5"),
    "C51": (["C51"], 30, [], True, "IV H: the held-out GENIE v3 tunes are not independent",
            "none; it qualifies the main result's fake-data validation", "yes: note Sec. 10.4"),
}


def density(d, w):
    return round(d / w * 1000, 2)


def evaluate(keys):
    removed, words = set(), 0
    for k in keys:
        c = CANDIDATES[k]
        removed |= set(c[0])
        words += c[1]
    return BASE["distinct"] - len(removed), BASE["words"] - words


def valid(keys):
    return all(r in keys for k in keys for r in CANDIDATES[k][2])


def search():
    names = list(CANDIDATES)
    hits, best_free = [], None
    for n in range(len(names) + 1):
        for combo in itertools.combinations(names, n):
            if not valid(combo):
                continue
            d, w = evaluate(combo)
            if density(d, w) <= TARGET:
                hits.append((n, combo, d, w))
            if not any(CANDIDATES[k][3] for k in combo):
                if best_free is None or density(d, w) < density(*best_free[1:]):
                    best_free = (combo, d, w)
    hits.sort(key=lambda h: (h[0], sum(CANDIDATES[k][3] for k in h[1]), -h[3]))
    return hits, best_free


def main(out=None):
    hits, free = search()
    d_all, w_all = evaluate(tuple(CANDIDATES))
    res = {"base_after_20_moves": dict(BASE, distinct_per_1k=density(BASE["distinct"], BASE["words"])), "target": TARGET,
           "every_candidate": {"distinct": d_all, "words": w_all, "distinct_per_1k": density(d_all, w_all)},
           "best_without_referee_keep": {"candidates": list(free[0]), "distinct": free[1], "words": free[2],
                                         "distinct_per_1k": density(free[1], free[2])},
           "minimum_sets": [{"candidates": list(c), "n": n, "distinct": d, "words": w,
                             "distinct_per_1k": density(d, w),
                             "referee_keep_moved": [k for k in c if CANDIDATES[k][3]]}
                            for n, c, d, w in hits if n == hits[0][0]] if hits else [],
           "candidates": {k: {"removes": v[0], "words": v[1], "requires": v[2], "referee_keep": v[3], "loses": v[4],
                              "cited_by": v[5], "note_holds": v[6]} for k, v in CANDIDATES.items()}}
    if out:
        Path(out).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "candidates"}, indent=1, ensure_ascii=False))


def self_test():
    ok = density(44, 7484) == 5.88
    ok &= not valid(("IVB",)) and valid(("IVB", "IVC"))
    d, w = evaluate(("IVE",))
    ok &= d == 44 and w == 7484 - 465 and density(d, w) > density(44, 7484)  # a caveat-free move raises the density
    d, w = evaluate(("IVE+IIIA:C20", "IVE", "IIIA"))
    ok &= d == 42
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(base density; a dependency is enforced; moving a section that "
          "carries no caveat RAISES distinct per 1k; a bonus counts only with its partners)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main(*[a for a in sys.argv[1:2]])
