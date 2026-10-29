"""Build agy's pairs for batch R (app_release.tex) from apply_n4.REL and the sources (nothing retyped), and a control
copy with one strengthening planted per pair.

usage: python3 -I make_pairs_r.py <worktree> <base-rev> <outdir>

BEFORE is the edited sentence at <base-rev>; AFTER is it with the pair applied. The CONTEXT is the evidence the fix
rests on: the claim table's row for that claim (release-claims.md), or, for R2-R4, the note's own statement that the
sixteen-cell covariance is a separate product."""
import re
import subprocess
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
N4 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(N4))
import apply_n4  # noqa: E402
from check_ledger import printed, sentences  # noqa: E402

base = subprocess.run(["git", "-C", str(W), "show", f"{BASE}:docs/analysis-note/app_release.tex"], capture_output=True,
                      text=True, check=True).stdout
table = (N4 / "release-claims.md").read_text()
fv = printed((W / "docs/analysis-note/sec_fived16.tex").read_text())
sep = next(s for s in sentences(fv) if s.startswith("It is a separate product from the configuration-(a)"))


def row(rl):
    hit = [l for l in table.splitlines() if l.startswith(f"| {rl} |")]
    assert len(hit) == 1, rl
    return re.sub(r"\s+", " ", hit[0])


CTX = {"RL21": row("RL-21"), "RL27": row("RL-27"), "RL39": row("RL-39"), "RL59": row("RL-59"),
       "RL45": "The record's copy is at /global/cfs/cdirs/m3246/josephrb (RECORD-20261010-ost61-hashed-and-data-addition.md "
               "sec. 3), the analysis group's NERSC project storage, not MINERvA collaboration storage. " + row("RL-60"),
       "R2": "The note: \"" + sep + "\"", "R3": "The note: \"" + sep + "\"", "R4": "The note: \"" + sep + "\""}
PLANT = {"RL21": ("which neither this note nor the article now prints", "which the article prints as its Fig. 3"),
         "RL27": ("drawn for that earlier version", "drawn for every version of the article"),
         "RL39": ("of that earlier version", "of the current article"),
         "RL59": ("(2,307 AnaTuples and 67 flux, reweight and parameter files)", "(all of them AnaTuples)"),
         "RL45": ("on NERSC project storage", "on MINERvA collaboration storage and on tape"),
         "R2": ("of the configuration-(a) central value and its", "of every result in this note and its"),
         "R3": ("of the configuration-(a) central value (", "of every result in this note ("),
         "R4": ("of the configuration-(a) central value is the file", "of every result in this note is the file")}
pairs = []
ss = sentences(printed(base))
for eid, _f, old, new in apply_n4.REL:
    po = printed(old)
    hit = [s for s in ss if po in s]
    assert len(hit) == 1, (eid, len(hit))
    pairs.append((eid, hit[0], hit[0].replace(po, printed(new))))
NOTE = ("(Each pair is one sentence of an analysis note's release appendix, BEFORE and AFTER a correction. The CONTEXT "
        "is the evidence from a check of the release package against the appendix; it is accepted as correct. Judge "
        "AFTER against BEFORE read with its CONTEXT: does AFTER state anything the CONTEXT does not support, state it "
        "more strongly, or mislead?)")
O.mkdir(parents=True, exist_ok=True)
for name, plant in (("pairs.txt", False), ("pairs-control.txt", True)):
    out = []
    for n, (eid, before, after) in enumerate(pairs, 1):
        if plant:
            o, nn = PLANT[eid]
            assert o in after, (eid, o)
            after = after.replace(o, nn, 1)
        out.append(f"Q{n}.\nCONTEXT: {CTX[eid]}\nBEFORE: {before}\nAFTER: {after}\n")
    (O / name).write_text(NOTE + "\n\n" + "\n".join(out), encoding="utf-8")
(O / "KEY.txt").write_text("\n".join(f"Q{n}\t{eid}" for n, (eid, _, _) in enumerate(pairs, 1)) + "\n")
print("pairs written:", len(pairs), "; control plants in each")
