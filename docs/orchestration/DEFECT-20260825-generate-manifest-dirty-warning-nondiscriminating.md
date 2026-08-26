# DEFECT 2026-08-25 — `generate_manifest.py`'s DIRTY warning does not discriminate

Filed on Joseph's ruling 4 of 2026-08-25 as an **owned tooling defect with controls**, not as a
caveat and not as a disclosure. It is repairable, and filing it does not discharge it.

Found by the independent comparator-repair lane while filing its own F-14 omission; controls
constructed and run by the publication close-out lane.

## CITABLE FOR

- The measurement that the DIRTY warning's text and exit status are **identical** whether the dirty
  paths are staged for the same commit or not.
- The negative control establishing the warning is not simply always-on.
- The claim that the warning's advice is **false** in the one case where the F-14 coupling requires a
  dirty regeneration.

## NOT CITABLE FOR

- Any Gate-2 clause. **This does not alter Gate 2's FAIL**, which stands for the reasons in
  `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`.
- Any part of the D-3 comparator repair. This defect is in a **different tool** and ruling 4 states
  it is not part of that completed repair. Do not expand the D-3 repair around it by implication.
- Excusing any F-14 omission. A misleading instrument is a cause, not a defence; the four omissions
  filed in `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` remain omissions.

## 1. The defect

`generate_manifest.py` emits, when any tracked path in the inventory scope is dirty:

> `WARNING: N tracked path(s) in the inventory scope are DIRTY, so their
> lines/bytes/inbound_count describe the WORKING TREE, not any commit: <paths>`

That sentence is true in general and **false in exactly the case where F-14 / §7.0.7 requires a
dirty regeneration** — when every path is staged and about to be committed together, the working
tree *is* the commit being built. The warning has no arm separating:

- **correct procedure** — dirty because the paths are staged and going in with the manifest, and
- **the hazard** — dirty because the paths are not being committed at all.

So it fires identically on the procedure the contract demands and on the mistake the contract
forbids, and it advises against the correct one.

## 2. Controls

Run in a throwaway detached worktree at `a06ca52e`, `root_6_28` python, never pushed. **The only
variable is staged-ness**: the same already-tracked file (`docs/orchestration/CATALOG.md`, in the
inventory scope) receives the same edit in both arms.

An earlier attempt used a *new* file for one arm and an existing file for the other. That confounded
staged-ness with path-set membership and produced a spurious "it discriminates" result — the texts
differed only because the counts did (2 vs 1). It is recorded here because the malformed version is
the one that looks like a clean refutation.

| Arm | Condition | rc | Warning |
|---|---|---|---|
| **0 — negative control** | clean tree | 0 | **absent** |
| **A — correct procedure** | edit STAGED | 0 | `WARNING: 1 tracked path(s) … : docs/orchestration/CATALOG.md` |
| **B — the hazard** | identical edit, NOT staged | 0 | `WARNING: 1 tracked path(s) … : docs/orchestration/CATALOG.md` |

- Arm 0 fires nothing, so the instrument **can** be silent — the A/B identity is not an artifact of
  an always-on warning. This is the arm that makes the other two mean something.
- A and B are **byte-identical in warning text and equal in exit status**.

**Conclusion, in the direction the guard acts:** a lane cannot use this output to determine whether
it is about to break the F-14 coupling, because the output is the same either way.

## 3. Measured consequence

Six F-14 coupling omissions were committed on 2026-08-25 across two lanes while this warning was
being read as guidance — four by the publication close-out lane (`30ede740`, `a3ed8631`, `38a7b16b`,
`109bb130`) and two by the comparator-repair lane (`c8a29082`, `3dbca981`). The comparator-repair
lane's own recorded reasoning for one of them was "commit sources first so the counts describe a
commit, not a working tree" — which is this warning's sentence, applied faithfully, producing the
violation.

That does not excuse the omissions and this record does not offer it as an excuse. It establishes
that the instrument's advice and the contract's requirement point in opposite directions in a case
that arises routinely.

## 4. What a repair has to do, without prescribing how

The repair is **not** to delete the warning: arm 0 shows it is correctly silent on a clean tree, and
the general case it warns about is real. What it lacks is an arm distinguishing staged-and-going-in
from not. Whoever implements this must produce, at minimum:

- an arm that FIRES on the hazard (dirty, not staged),
- an arm SILENT on correct procedure (dirty, fully staged, about to be committed), and
- the opposite-direction arm: dirty, staged, and *not* committed — where staging is not sufficient.

The third is the one an obvious implementation will miss.

**Ownership is unassigned.** Under the separation ruling 3 established for the comparator, the
implementer and the grader must be different parties. This lane is eligible to implement (it did not
author `generate_manifest.py`) but may not then grade its own work. `generate_manifest.py` has many
callers, so a behaviour change to it is wider than it looks.

## 5. Cited artifacts

Instrument: `docs/orchestration/generate_manifest.py`, warning emitted from `main()`. Run under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3` (3.11.14); the system `python3` is 3.6.15
and cannot parse the file.

Controls: `dirty_controls2.sh`, run at `a06ca52e`. Probe worktrees removed; nothing pushed.

Related: `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` (four omissions, this lane),
`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md` (two, that lane),
`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` §§13–14.
