# REF-G1 BINDING 1, step one: the 16-cell binned head-to-head's design (director, 2026-11-05)

**Binds** [`REF-G1-DECLARATION.md`](REF-G1-DECLARATION.md), sha256
`1ea76a3b263b13319ff9910ab4165fb094953812be7d27c2e45aad98c06e7497`, as merged in PR #763 at
**M = `ddbc43e42f7b1ae4687f024d62baadda99a2aedf`** (PR head `8c8f0faa`).

**Commissioned by** `DECISION-20261104-joseph-referee-analysis-commission.md` (g1). R1's bars follow
`DECISION-20261104-joseph-g1-r1-calibrated-bars.md`.

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above. The merge of main into the branch (`8c8f0faa`)
  left the declaration unchanged against the audited text: `git diff 49d82424 8c8f0faa` on that file is empty.
- **The audit** (coverage-5b-audit; #763 comments 6645264150 and 6649849679, then the deltas to 0fca1c70 and
  f6cd48468):
  - **B1:** R1's χ² bars on a Hotelling null went to Joseph and were decided. The calibrated null was implemented
    to the decision's items 2–6 and checked.
  - **G-draw** goes through (e)'s jitter step.
  - **The jitter-skip mutant** is recorded as equivalent, with the auditor's proof. It is still run once as an
    expected survivor (the director, 2026-11-04). The required mutant is "membership refusal removed from g1's
    builder", killed by the rc-5 refusal test.
  - Nothing else blocks.
- **The text after the last audited head** (`f6cd48468` to `49d82424`) adds only the expected-survivor line, as ruled.

## Rulings

1. **Step one is bound: the design at M.** Nothing runs before step two binds the code.
2. **The code lane is `limitations-catalog`.** It writes `nd-unfolding/ref_g1/` as §7 says, with:
   - the tests;
   - the mutation harness, every mutant §7 lists, and the expected survivor;
   - a receipt.

   The code then goes to coverage-5b-audit and comes to the director for step two, which pins its blobs.
3. **The cluster lane is `limitation-resolver`.** It does not write g1's code.
   - **Preconditions 1–3 of §7 come first:** the (e) and IBU input listing, and the bank and detector listing with
     atime, on a DTN, at 0 node-h, with O_NOATIME. Their connect's sha256 comes to the director before it runs.
   - These may run before step two. They read and list only.
   - **They are timely.** The 12 per-playlist universe loops are exposed on pscratch from 2026-11-09, and the bank's
     and the detector dump's atime are unknown until the listing. A listing showing a missing or differing file stops
     and comes to the director, as §7 says. Nothing is rebuilt.
4. **The price.**
   - The cap is **5.0 CPU node-h**, CPU only, every job under 12 h, written `HH:MM:SS` in every `--time`.
   - Each connect prints `scontrol` TimeLimit after submission and cancels on a mismatch (FD-STAB-BINDING-1-A1's
     correction, applied to every campaign).
   - The lane times one universe unit first. A projection above the cap stops and reports, and does not shrink the
     set.
   - The cap is far below half the balance. This is an operational go-ahead within the standing grant, and it is
     reported to Joseph with this binding.
5. **R1's bars are committed before the central Δ is formed** (`bars.json` with its sha), as the decision and §4
   require. A run that forms Δ first is INVALID.
6. **The paper and the note.** §5's licences bind. Any sentence from g1 goes through the paper lane, a PRD-referee read
   of the exact wording, and Joseph, before merge. That includes g0, the motivation question.

Nothing is submitted, deposited or tagged.
