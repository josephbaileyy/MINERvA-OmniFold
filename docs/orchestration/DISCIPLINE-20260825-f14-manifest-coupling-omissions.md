# DISCIPLINE 2026-08-25 — F-14 / §7.0.7 manifest-coupling omissions

Filed by the publication close-out lane, on Joseph's instruction of 2026-08-25, against its own
commits. This is a discipline record, not a defect disclosure and not a gate document.

## CITABLE FOR

- **Four** F-14 coupling omissions by this lane on 2026-08-25, each named with its commit and what
  it left stale. It was three until the fourth was found by applying to my own commits the standard
  I had applied to a peer's; see §2.1.
- The measurement that the `intended`->`tracked` flip is **avoidable in one pass**, which is what
  makes the fourth an omission rather than an inherent cost (§2.1).
- The measurement that `generate_manifest.py --check` returned **rc=1** at `38a7b16b` in a clean
  detached worktree.
- The mechanism by which one of these omissions became invisible: another lane's regeneration
  absorbed it.

## NOT CITABLE FOR

- Any Gate-2 clause. F-14 is not one of the nine, and nothing here changes the Gate-2 FAIL recorded
  in `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`.
- The pre-existing 23-row drift on `main`. That is a **different and unattributed** population, and
  it is **CLOSED** — see §4. Do not read this document as having accounted for it, and do not read it
  as an open item either.
- Any other lane's coupling omission. One is named in §4.1 and is deliberately **not** counted here.
- The current state of `MANIFEST.tsv`. That is a measurement with a date, not a property.

## 1. The obligation

F-14 requires every §6 row discharged in the same commit as the repair, **plus** §7.0.7(1):
`generate_manifest.py --check` = 0. Because a doc-only or tool-only commit still moves
`MANIFEST.tsv` — the manifest records each tracked path's line and byte counts, and indexes itself —
the regeneration is **coupled into the same commit**. Regenerating later produces a correct manifest
and still fails the coupling.

**That coupling is a COMPOSITION, and this document originally presented it as if it were contract
text.** F-14's same-commit language is scoped to §6's rows. §7.0.7(1)'s test is `--check` = 0 *at the
graded sha*, and §7.0.7 does not itself name the manifest among §6's rows. The sentence beginning
"Because" above is an inference I drew, not a quotation. The composition is correct on the merits —
§7.0.7's grounds are a complaint about a *published* sha exiting 1, which is precisely what an
uncoupled commit produces — but a lane reading only the contract can satisfy §7.0.7's letter at the
graded sha while breaking the coupling at every commit before it. That is a **discoverability gap in
the contract, not an excuse**, and it was identified by the comparator-repair lane, which declined to
use it as one. The obligation belongs where the contract states it; recording that here does not put
it there.

## 2. The omissions, as measured

Joseph named `38a7b16b`. Measured, there are **three**. Recording only the one named would have made
a partial enumeration look complete, so all three are below.

| Commit | Path changed | Manifest regenerated in-commit | What it left stale |
|---|---|---|---|
| `30ede740` | `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | **NO** | the script's line/byte counts |
| `a3ed8631` | `docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json` | **NO** | **an entire row absent** — not a stale count |
| `38a7b16b` | `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | **NO** | the script's line/byte counts |
| `109bb130` | decision doc + overrides + CATALOG | regenerated, but see §2.1 | **rc=1 at its own sha** |
| `dce8e8cc` | second-pass regeneration | YES | — |

Direct measurement of the worst one: `git show a3ed8631:docs/orchestration/MANIFEST.tsv` contains
**zero** rows matching `f17b-k0-aa67c426`. The record I had just filed was, at that commit, invisible
to the router.

Direct measurement of the gate state: at `38a7b16b`, in a **clean detached worktree** (not my working
tree, because a gate can fail on a dirty tree for reasons that have nothing to do with the commit),
`generate_manifest.py --check` returns **rc=1**, `OUT OF DATE`, rows=526.

All of these are attributable to the publication close-out lane. No peer lane contributed to them.

## 2.1 A fourth, found by applying my own standard to myself

I raised `c8a29082` against the comparator-repair lane. It accepted the finding, and in answering it
asserted that for a **new** path the `intended`->`tracked` flip is irreducible — no single commit can
carry it, because `tracking` records whether the path is committed and the commit does not yet exist.
It cited my own `109bb130` -> `dce8e8cc` pair as the documented compliant shape.

**I measured the claim instead of accepting the compliment, and it is false.**
`generate_manifest.py:92` determines tracked-ness with `git ls-files`, which reads the **INDEX, not
HEAD**. Staging the new path *before* regenerating therefore classifies it `tracked` in a single
pass. Probe, run in a throwaway detached worktree at `62a40194` and never pushed: create a new doc,
add its override row and CATALOG entry, `git add` the new path, regenerate, commit all four together
— probe sha `89a5464f`, whose row reads `tracking=tracked`, and `--check` returns **rc=0 in a
separate clean worktree at that sha**, in one pass.

So the two-commit shape is a **convention, not a constraint**, and the consequence lands on me:

**`109bb130` returns rc=1 at its own sha** (measured, clean detached worktree). My §2 table marked it
`YES`. By the standard I had just applied to a peer's `c8a29082`, it is an omission, it was
avoidable, and I had recorded it as an example of compliance. That makes **four**, not three.

The failure is not the extra commit. It is that I graded a peer by a test I had not run against
myself, and the version of the rule I published was the one my own work happened to satisfy. The
peer's "irreducible" defence and my "compliant pair" framing were the same unmeasured belief, held
from opposite sides, and neither of us checked it until one of us was accused.

## 3. Why it stayed invisible, which is the part worth keeping

The missing row from `a3ed8631` was added by **the independent Gate-2 grader's** commit `a3000487`,
whose own regeneration swept it up as a side effect of doing its work correctly.

The consequence generalises past this incident: **a later "the manifest is current" observation says
nothing about whether any particular commit complied.** Any lane that regenerates absorbs every
upstream omission silently, so compliance is only measurable *at the commit*, in a clean worktree,
and only before someone else regenerates. By the time I looked at `MANIFEST.tsv` and found my record
correctly classified `MACHINE / state-artifact / generated`, my omission had already been repaired by
someone else and there was nothing left to see.

I did not detect any of the three. The first was surfaced by comparing counts during an unrelated
regeneration; the rest by measuring on Joseph's instruction.

## 4. Explicitly not accounted for here

`generate_manifest.py --check` returned rc=1 in a clean detached worktree at `e428a645` with 23
rows of drift, measured by the Gate-2 grader before any of my commits in this sequence. That is
**pre-existing committed drift from a population I have not attributed**, and it is named here only
so that this document is not mistaken for a complete account of F-14 drift on `main`.

**It is CLOSED, and an earlier version of this section implied otherwise.** Measured in clean
detached worktrees: rc=1 at `e428a645` (525 rows), then rc=0 at `a0d0e5a1` (526), `dce8e8cc` (527),
`65f95600` (527) and `7d0776b8` (528). The Gate-2 grader's `a0d0e5a1` closed it and it has stayed
closed. I have also now **derived** the 23 rather than relaying it: regenerating at `e428a645` and
diffing the committed manifest gives 23 differing rows, **5 of which are absent from the committed
file entirely** — one figure covering two kinds of drift.

The attribution point survives the correction and is sharper for it: because `a0d0e5a1` cleared
everything upstream of it, **any drift in a commit after `a0d0e5a1` belongs to that commit's
author**, with no pre-existing pool to attribute it to.

### 4.1 A second lane's instance, which is that lane's to file

`c8a29082` (independent comparator-repair lane) changed two tracked paths —
`compare_m1_m6.py` and `test_compare_m1_m6.py` — and did not regenerate `MANIFEST.tsv` in that
commit; `65f95600` regenerated afterwards. That is the same coupling break catalogued in §2 and it
is **not counted in this document's four**, because attribution belongs to the lane that made it
and a discipline record that absorbs other lanes' instances stops being an accurate account of
anyone. Named here so this section cannot be read as evidence that no other instance exists.

**FILED by that lane at `34c16f16`** —
`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md`. This is no longer an open referral. It
verified my finding rather than accepting it, disproved its own stated justification with a probe,
recorded a second instance (`3dbca981`, rc=1) committed while filing the first, and replaced a claim
of its own that went false within minutes rather than softening it. Its ledger, which I re-measured
independently and reproduce exactly: `c8a29082` rc=1, `65f95600` rc=0, `3dbca981` rc=1, `34c16f16`
rc=0.

Its `3dbca981` and my `109bb130` are the **same** instance of the same false belief (§2.1). I do not
count its instances and it does not count mine, but the belief was shared and neither record would
have found it alone.

## 5. Remediation, and what it does not do

`109bb130` and `dce8e8cc` regenerated the manifest. Measured **after** each commit returned rather
than before it: rc=0 at `dce8e8cc` with `tracking=tracked:527`, and rc=0 at `7d0776b8` with
`tracked:528`. Both figures are as-of their commit, not a current state — the row count rises with
every added path, so a bare "527" would rot immediately.

**That repairs the manifest state. It does not erase the original gap**, and this record exists
because the repaired state would otherwise be the only surviving evidence — which would read as
compliance.

**The remedy going forward is one pass, not two:** stage every path including the new one, regenerate
while dirty, commit all of it together. Measured to work (§2.1). Note that
`generate_manifest.py` emits a DIRTY warning in exactly that situation — it is true in general and
inapplicable in the one case where the coupling *requires* a dirty regeneration, and it has no arm
distinguishing "dirty and about to be committed alongside" from "dirty and not". It therefore fires
identically on correct procedure and on the hazard. That is a candidate strengthening of the
instrument; neither this lane nor the comparator-repair lane changed it, because it has many callers
and the call is not ours.

## 6. Cited artifacts

Commits: `30ede740`, `a3ed8631`, `38a7b16b` (the omissions) · `109bb130`, `dce8e8cc` (this lane's
compliant pair) · `a3000487`, `a0d0e5a1` (the grader's, which absorbed the `a3ed8631` gap) ·
`e428a645` (where the unattributed 23-row drift was measured, and which `a0d0e5a1` closed).

Instrument: `docs/orchestration/generate_manifest.py`, run under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3` (3.11.14). The system `python3` is 3.6.15
and cannot parse it — a `SyntaxError` on `from __future__ import annotations`, which through a pipe
reads as rc=0 and would report a false pass.
