"""note_probes.py -- does the analysis note print each fact a candidate move would take out of the paper?

usage: python3 -I note_probes.py NOTE_BLIND_TXT [OUT.json]

NOTE_BLIND_TXT is the note's blinded text at the same commit (remeasure.py writes it as blind/ours-note.txt). Each
probe is one fact the paper prints in the moved text, as the value or phrase that states it, searched in the note's
text with whitespace collapsed. A fact with no hit must be added to the note before its move ("NOTE FIRST"). A hit
shows the note prints the value or phrase, not that the note's sentence says exactly what the paper's did.
"""
import json
import re
import sys
from pathlib import Path

# move -> [(the fact as the paper states it, a regex for the note's text)]
PROBES = {
    "IIIA": [("a 10% median half-width precision target", r"precision target"),
             ("envelope median about 10-13% per cell", r"10–13"),
             ("the envelope is a diagnostic, not an interval", r"envelope.{0,80}(not an interval|diagnostic)")],
    "IVBC": [("integrated ratio 1.010 to the published result", r"1\.010"),
             ("standardized-difference RMS 0.535", r"0\.535"),
             ("chi2/ndf 2.27 against the published covariance", r"2\.27"),
             ("pseudo-inverse condition number 1.5e12", r"condition number"),
             ("the shape difference's source not identified", r"shape difference.{0,60}(not been identified|unknown|not identified)"),
             ("learner chosen after comparison with the published result", r"learner was chosen|chosen after"),
             ("exact-split differs by a median 1.03% per bin, maximum 17.6%", r"1\.03 ?%.{0,200}17\.6|17\.6.{0,200}1\.03"),
             ("187 systematic universes", r"187"),
             ("published flux uncertainty 4.01% exceeds ours", r"4\.01"),
             ("training-seed block from five seed settings", r"five seed|seed settings"),
             ("run-period step of about 7% near 8 GeV/c", r"step of \(\+6\.89|6\.89 ± 0\.46\)% at 8 GeV/c"),
             ("run-period block 2.0% on the integrated cross section", r"1\.97 ?% on the integrated"),
             ("no statement about the published analysis's residual (iteration counts differ)", r"no statement about the size|iteration counts differ"),
             ("an earlier statistical band undercovered in its tails", r"undercover")],
    "IVC": [("187 systematic universes", r"187"),
            ("published flux uncertainty 4.01% exceeds ours", r"4\.01"),
            ("training-seed block from five seed settings", r"five seed|seed settings"),
            ("run-period block 2.0% on the integrated cross section", r"1\.97 ?% on the integrated"),
            ("no statement about the published analysis's residual (iteration counts differ)", r"no statement about the size|iteration counts differ")],
    "IVDbkg": [("purity-based subtraction biased up to 4% at highest W", r"up to 4 ?%|4 ?% in simulation"),
               ("2D closure: purity estimate up to 5.9 statistical SD", r"5\.9"),
               ("refined estimate within 0.44 in every cell", r"0\.44"),
               ("14 of the 205 cells more than one statistical SD apart", r"14 of the 205"),
               ("the two treatments differ by at most 1.4% on data", r"at most 1\.4 ?%|1\.4 ?% on data")],
    "IVE": [("up to 74% at high W", r"74 ?%"),
            ("16-31% in the most affected cell", r"16 ?% to 31 ?%"),
            ("within the total uncertainty in about half of those cells", r"about half"),
            ("an earlier covariance fails its specified acceptance criteria", r"acceptance criteria"),
            ("earlier estimator's 68% intervals cover as low as 0.06", r"0\.06")],
    "IVF": [("rounding scatter median 0.23% per joint cell", r"0\.23 ?%"),
            ("against a median data-bootstrap statistical uncertainty of 0.37%", r"0\.37 ?%"),
            ("up to 2.6 (and 2.5 for the development variant) statistical SD", r"at most 2\.6.{0,120}2\.5"),
            ("fails the data-stability requirement (median 0.3, maximum 1.0)", r"data-stability")],
    "VC": [("3D and 4D central values carry no uncertainties", r"no 3D or 4D covariance|central values without u"),
           ("generators underpredict at low Eavail, the low-recoil region", r"low-recoil discrepancy")],
}


def main():
    text = re.sub(r"\s+", " ", Path(sys.argv[1]).read_text(errors="replace"))
    out = {}
    for move, facts in PROBES.items():
        out[move] = [{"fact": f, "pattern": p, "note_prints": bool(re.search(p, text, re.I))} for f, p in facts]
        for r in out[move]:
            print(f"{move:7s} {'yes ' if r['note_prints'] else 'NOTE FIRST'}  {r['fact']}")
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
