#!/usr/bin/env python3
r"""US spelling in printed text (Joseph writes American English; the director, 2026-11-17).

usage: check_spelling_us.py FILE.tex [FILE.tex ...]   exit 1 on any British form in printed text, with its US form
       check_spelling_us.py --self-test                each planted British form is caught; the mutant (no inflections) misses

Printed text only. Comments (% ...) are removed, and so are the arguments of commands that print no prose: \label, \ref,
\cite, \url, \href's URL, \includegraphics, \input, \fvval, \nsec, \napp, \psec, \ssec's label, \texttt (code and file
names) and \newlabel. Command names are removed too.

The list is explicit, with its inflections generated. It is not a suffix rule: a rule like "-ise" would also flag
"precise", "otherwise" and "rise". The groups are -our, -ise/-isation, -yse, -re, doubled -ll-, and grey, artefact,
towards and the other -wards forms (afterwards, backwards, ...; the cold read of d5363e09e), whilst and amongst
(style). "analyses" is not flagged, because it is also the US plural of analysis. A word in
ALLOW (a proper name or a quoted title) is skipped.
"""
import re
import sys

OUR = ["colour", "behaviour", "neighbour", "favour", "honour", "labour", "flavour", "harbour", "rumour", "humour",
       "vapour", "endeavour", "odour", "armour", "savour", "vigour", "rigour", "tumour", "candour", "fervour"]
ISE = ["normal", "regular", "organ", "recogn", "minim", "maxim", "optim", "character", "parametr", "parameter", "summar",
       "emphas", "real", "util", "standard", "random", "general", "linear", "symmetr", "discret", "binar", "priorit",
       "categor", "visual", "final", "initial", "stabil", "penal", "marginal", "local", "factor", "hypothes", "critic",
       "special", "digit", "synthes", "central", "polar", "neutral", "author", "custom", "vector", "serial",
       "token", "harmon", "memor", "modern", "capital", "rational", "theor", "item",
       "jeopard", "global", "legal", "mobil", "fertil", "steril", "subsid", "sympath", "apolog", "familiar", "formal",
       "homogen", "industrial", "internal", "orthogonal", "personal", "quant", "unitar"]
YSE = ["analys", "catalys", "paralys", "dialys"]
RE = {"centre": "center", "metre": "meter", "fibre": "fiber", "litre": "liter", "calibre": "caliber",
      "spectre": "specter", "theatre": "theater", "sabre": "saber", "lustre": "luster", "meagre": "meager"}
LL = ["label", "model", "travel", "cancel", "signal", "level", "total", "channel", "fuel", "counsel", "tunnel",
      "marshal", "model", "pedal", "dial", "equal", "rival", "funnel", "jewel", "shovel", "tranquil"]
OTHER = {"grey": "gray", "greys": "grays", "greyed": "grayed", "artefact": "artifact", "artefacts": "artifacts",
         "towards": "toward", "afterwards": "afterward", "backwards": "backward", "forwards": "forward",
         "upwards": "upward", "downwards": "downward", "inwards": "inward", "outwards": "outward",
         "whilst": "while", "amongst": "among", "programme": "program", "programmes": "programs",
         "catalogue": "catalog", "catalogues": "catalogs", "dialogue": "dialog", "licence": "license", "defence": "defense",
         "offence": "offense", "judgement": "judgment", "ageing": "aging", "sceptical": "skeptical", "aluminium": "aluminum",
         "manoeuvre": "maneuver", "enrol": "enroll", "fulfil": "fulfill", "skilful": "skillful", "wilful": "willful",
         "tyre": "tire", "cheque": "check", "practise": "practice", "practised": "practiced", "learnt": "learned",
         "spelt": "spelled", "acknowledgement": "acknowledgment", "acknowledgements": "acknowledgments"}
ALLOW = set()     # proper names and quoted titles that keep their spelling, one entry per word, with its reason


def build(inflect=True):
    m = dict(OTHER)
    for w in OUR:
        us = w[:-2] + "r"
        for suf in ([""] + (["s", "ed", "ing", "al", "ally", "able", "ite", "ites", "ful", "less", "hood", "hoods",
                             "ly", "ing"] if inflect else [])):
            m[w + suf] = us + suf
    for stem in ISE:
        for b, u in ([("ise", "ize")] + ([("ised", "ized"), ("ises", "izes"), ("ising", "izing"),
                                          ("isation", "ization"), ("isations", "izations"), ("iser", "izer"),
                                          ("isers", "izers")] if inflect else [])):
            m[stem + b] = stem + u
    for stem in YSE:
        for b, u in ([("e", "e")] + ([("ed", "ed"), ("ing", "ing"), ("er", "er"), ("ers", "ers")] if inflect else [])):
            m[stem + b] = stem[:-1] + "z" + u        # analyse -> analyze ("analyses" is not listed: the US plural)
    for b, u in RE.items():
        m[b] = u                                    # centre -> center
        if inflect:
            m[b + "s"] = u + "s"                    # centres -> centers
            m[b[:-1] + "ed"] = u + "ed"             # centred -> centered
            m[b[:-1] + "ing"] = u + "ing"           # centring -> centering
    for w in LL:
        for suf in (["led", "ling", "ler", "lers"] if inflect else ["led"]):
            m[w + suf] = w + suf[1:]                # labelled -> labeled
    for k in [k for k in m if k == m[k]]:
        del m[k]
    return m


BRIT = build()


def printed(t):
    t = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.split("\n"))
    t = re.sub(r"\\(label|ref\*?|eqref|cite[a-z]*|url|includegraphics|input|include|fvval|nsec|napp|psec|texttt|"
               r"newlabel|holdrec|lrval|bibliographystyle|bibliography|usepackage|documentclass)(\[[^]]*\])?\{[^}]*\}",
               " ", t)
    t = re.sub(r"\\(ssecc?|stab|sfig)\{([^}]*)\}\{[^}]*\}", r" \2 ", t)
    t = re.sub(r"\\href\{[^}]*\}", " ", t)
    return re.sub(r"\\[A-Za-z]+", " ", t)


def hits(text, table=None):
    table = BRIT if table is None else table
    out = []
    for n, line in enumerate(printed(text).split("\n"), 1):
        for m in re.finditer(r"[A-Za-z]+", line):
            w = m.group(0)
            lw = w.lower()
            if lw in table and lw not in ALLOW:
                out.append((n, w, table[lw]))
    return out


def self_test():
    ok = True
    plant = ("The centred shape is labelled. We normalised the colour and analysed it, towards a grey artefact afterwards.\n"
             "% a comment's colour is not printed\n\\label{sec:colour} \\texttt{normalise.py} The analyses are fine.\n"
             "Precise, otherwise, rise and wise are not British forms. The behaviour of neighbouring cells.")
    got = sorted({w for _, w, _ in hits(plant)})
    want = sorted(["centred", "labelled", "normalised", "colour", "analysed", "towards", "grey", "artefact",
                   "behaviour", "neighbouring", "afterwards"])
    if got != want:
        print("self-test: got", got, "want", want); ok = False
    if hits("Precise, otherwise, rise, wise, analyses, four hours, your parameters, metres") != \
            [(1, "metres", "meters")]:
        print("self-test: a false hit or a miss on the control line:", hits("Precise, otherwise, rise, wise, analyses, four hours, your parameters, metres")); ok = False
    mutant = build(inflect=False)
    if sorted({w for _, w, _ in hits(plant, mutant)}) == want:
        print("self-test: the mutant without inflections is not caught"); ok = False
    print("CHECK-SPELLING-US SELF-TEST ::", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if argv == ["--self-test"]:
        return 0 if self_test() else 1
    bad = 0
    for p in argv:
        for n, w, us in hits(open(p, encoding="utf-8").read()):
            print(f"{p}:{n}: {w} -> {us}")
            bad += 1
    print(f"CHECK-SPELLING-US :: {'PASS' if not bad else 'FAIL'} ({bad} British form(s) in {len(argv)} file(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
