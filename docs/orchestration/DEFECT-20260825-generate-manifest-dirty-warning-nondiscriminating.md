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
from not.

**The discriminating information already exists and is thrown away.** Located 2026-08-25 by a fresh
advisory lane at `generate_manifest.py:328`, in `dirty_inventory_paths`:

    return sorted({line[3:].split(" -> ")[-1] for line in rows if not line.startswith("??")})

It runs `git status --porcelain` and then discards `line[:2]` — the XY code — in the same expression
that builds the set. The three states are all present in output the tool already has:

| porcelain XY | meaning | which case |
|---|---|---|
| `' M'` | dirty, NOT staged | **the hazard** |
| `'M '` | dirty, fully staged | **correct procedure** |
| `'MM'` | staged AND further unstaged edit | **staging is not sufficient** |

A fourth, directly F-14-shaped: `MANIFEST.tsv` showing `' M'` while its sources show `'M '` —
regenerated but not staged with them.

Minimum controls: an arm that FIRES on `' M'`, an arm SILENT on `'M '`, and the opposite-direction
arm on `'MM'`, which is the one an obvious implementation will miss.

**CORRECTION 2026-08-25 to this section's third control.** It previously demanded an arm for "dirty,
staged, and *not committed* — where staging is not sufficient." That conflated two different things:
`'MM'`, which is **observable at run time**, and "staged and then never committed", which is a
**future fact no implementation inside `generate_manifest.py` can observe**. As written the control
was unsatisfiable. The observable half is kept above; the unobservable half belongs at commit time as
a pre-commit check, not as a warning, and is out of this defect's scope.

**In scope, same defect family**, found while measuring the above: in default mode the tool silently
absorbs a peer's untracked files into the inventory and flips `--check` to rc=1, disclosing them only
under `--committed-only`. Measured on this shared checkout: default `--check` rc=1, rows=537,
`tracking=intended:4`, caused entirely by four untracked files a peer left in `docs/orchestration`;
`--check --committed-only` rc=0, rows=533. **That rc=1 is the instrument reporting, not a broken
manifest, and nobody should "repair" it.** (Superseded as a statement about `main`: those four paths
were committed hours later at `e30dbd45` *without* regenerating, so `main` then went rc=1 in **both**
modes for a genuinely different reason — `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md`
§4.2. The two rc=1s are indistinguishable from the exit status alone, which is this defect's shape.)
But the shape is identical to the DIRTY defect — the instrument holds the discriminating fact and
withholds it in the mode where it matters — so it belongs inside this repair rather than in a
separate filing.

**Ownership: an INDEPENDENT IMPLEMENTER. NOT the publication close-out lane.**

An earlier version of this section said the close-out lane was eligible "because it did not author
`generate_manifest.py`". That is the **tool-authorship** prong, and it is not the one ruling 3 turns
on. §6 of the decision record disqualifies that lane from repairing or grading `compare_m1_m6.py`
because it *authored the instrument's spec*. **This section is a specification** — it enumerates the
acceptance controls — and the close-out lane wrote it. By the rule that disqualified it from the
comparator, it is the spec author here and may be neither implementer nor grader.

A second, independent reason: that lane committed **four of the six** F-14 omissions this warning
contributed to, and §14 rules that confession is not validation. The belief that the instrument
misled it is the belief that excuses it.

The filing stays with the close-out lane (attribution belongs with the party that made the omission,
per §14). The repair goes elsewhere, and its grader must differ from its implementer.
`generate_manifest.py` has many callers, so a behaviour change is wider than it looks.

## 5. Cited artifacts

Instrument: `docs/orchestration/generate_manifest.py`, warning emitted from `main()`. Run under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3` (3.11.14); the system `python3` is 3.6.15
and cannot parse the file.

Controls: `dirty_controls2.sh`, run at `a06ca52e`. Probe worktrees removed; nothing pushed.

Related: `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` (four omissions, this lane),
`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md` (two, that lane),
`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` §§13–14.

## 6. DISPATCH (Joseph, 2026-08-25): the independent implementer is `codex-school`

**Assigned: `codex-school`.** **Constraint, as ruled:** it re-derives from **this defect record and
the artifacts**, and does **not** read the publication close-out lane's reasoning or the advisory
lane's analysis. *Hand over the record, not the analysis.*

So this document is the entire brief, deliberately. What it hands over, and how to treat each part:

- **Section 1 is a claim to VERIFY, not to inherit** -- that the warning's text and exit status are
  identical whether the dirty paths are staged for the same commit or not. **Re-measure it.** Do not
  cite section 2's table as its evidence: section 2 also records that the *first* attempt at those
  controls was malformed (it varied path-set membership alongside staged-ness) and produced a
  spurious "it discriminates", and the malformed version is the one that reads as a clean refutation.
- **Section 4 is the specification**: the three required arms -- FIRES on `' M'`, SILENT on `'M '`,
  and the opposite-direction arm on `'MM'` -- plus the recorded correction stating why an earlier
  third arm ("staged and then never committed") was **unsatisfiable** from inside
  `generate_manifest.py`. The mechanical locus at `generate_manifest.py:328` is named there; confirm
  it before relying on it, since a line number is dated.
- **Section 4's in-scope sibling**: default-mode `--check` silently absorbing another lane's
  untracked files. Same shape -- the instrument holds the discriminating fact and withholds it in the
  mode where it matters -- so it is inside this repair, not a separate filing.

**On `main`'s `--check` result, which changed under this lane's feet inside one day.** Two different
rc=1s existed, and only one of them is the sibling defect:

- At `17b79fca`: rc=1 under **default** mode, rc=**0** under `--committed-only`, caused entirely by
  four *untracked* files a peer had left in `docs/orchestration`. **That** one is the sibling defect
  above -- the instrument reporting -- and must not be "repaired".
- At `aaed392d` (`github/main`): rc=1 in **BOTH** modes, because `e30dbd45` committed those four
  paths without regenerating `MANIFEST.tsv`. That is a real F-14 coupling omission by a third lane,
  measured in `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.2 and regenerated by this
  lane's register-closure commit.

**Read the mode and the row counts; never the exit status by itself.** The two cases are
indistinguishable from rc alone, which is the same non-discriminating shape this whole defect is
about -- so do not build the repair's acceptance test on an rc comparison.

**Separation, both prongs:** the close-out lane may neither implement (it authored section 4, and
section 4 is a specification -- the same prong that disqualified it from `compare_m1_m6.py`) nor
grade (section 14 of the decision record, and it committed four of the six omissions this warning
contributed to). **The grader must be a third party: not `codex-school`, not the close-out lane.**

`generate_manifest.py` has many callers, so a behaviour change is wider than it looks. Nothing in
this dispatch authorizes compute, a Gate-2 filing, or a rehearsal; Gate 2 remains **FAIL**, and this
implementation is the third independent origin Joseph is holding it against.
