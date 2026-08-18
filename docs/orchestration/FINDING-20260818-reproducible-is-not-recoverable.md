# FINDING 2026-08-18 — "reproducible" is not "recoverable", and the receipt is tracked at every hop

**BEN-259.** Lane D (verifier). **Lane A found the chain** (`git ls-files` at the second hop) and
independently confirmed the `check-ignore` resolution and the oracle's two `np.load` sites at
`476ca897`; the hinge, the scratch-side facts and the retraction below are mine. A declined to host
this in its own block on the grounds that filing another lane's finding is what its `BEN-441` warns
about — correctly.

## The promise

`nd-unfolding/pet/powered_closure/.gitignore`, lines 1-4:

> *"…keep the heavy products out and the EVIDENCE in: the JSON receipts and the DONE sentinels are
> the whole point of the gate, **the multi-GB artifact and the Keras weights are reproducible from
> them plus the dump**."*

**That promise is true, and it is not the problem.** Saying so plainly matters, because the finding
is not "someone excluded something they shouldn't have."

## What it does not say

`CLM-012` is `VERIFIED-NUMERIC`, and re-running its verification means running
`nd-unfolding/pet/d2_acceptance_oracle.py`, which opens **two** files:

```
:58   ART  = .../powered_closure/POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz   :94  np.load(ART)
:61   DUMP = .../g2_fullevent/input/G2_FPS_MEFHC_P12.npz                       :99  np.load(DUMP)
```

| object | tracked? | where | size |
|---|---|---|---|
| the artifact | **no** — `powered_closure/.gitignore:6:*.npz` | `/pscratch` | 20,809,503 B |
| the dump | **no** — root `.gitignore:29:*.npz` | `/pscratch` | 9,897,374,636 B |

`CLAUDE.md`: *"Scratch is large but **purgeable** — anything irreplaceable needs a copy off scratch."*

> **The guarantee does not discharge the risk. It relocates it to a second object under identical
> exposure, and does not say so.** A lane reading that header learns *"excluding heavy products here
> is safe"* and **cannot learn from it what the safety is conditional on.**

## Why it is a class and not an instance: the receipt is tracked at every hop

```
git ls-files nd-unfolding/pet/powered_closure/   -> REPORT json, PREFLIGHT jsons, DONE sentinel
git ls-files nd-unfolding/g2_fullevent/input/    -> G2_FPS_MEFHC_P12_RECEIPT.json
```

**Both hops have the same shape: receipt tracked, payload not.** So a lane running `OI-130`'s
enumeration as written — *"is the backing artifact tracked?"* — finds a receipt at the artifact,
follows the reproducibility promise to the dump, and **finds a receipt there too.**

**It stops at every hop, and at no hop does it see that the payload is missing.** Each link
individually looks discharged. That is why this is not one tracked-report/untracked-input case; it is
a **chain** of them, and the enumeration's question cannot distinguish a discharged link from an
undischarged one.

## The detection rule

> **Follow the promise, not the object.** When an exclusion is justified by reproducibility,
> enumerate what the reproduction *consumes* and check the storage class of **each** — recursively —
> terminating only at something tracked, something off scratch, or a stated cost.

The existing question terminates at the first receipt. This one cannot, because a receipt is not a
terminator: it is a pointer to a payload whose storage class it does not state.

## Remedy

**A reproducibility promise must state its preconditions' storage class.** One sentence in the
header. It costs nothing, it is checkable, and it converts a claim a reader must trust into one a
reader can falsify. `CLAUDE.md`'s *"prefer the executable form of any rule you are tempted to write
down"* applies with the amendment `BEN-255` added: **an executable form still has to say where it
executes** — and a promise still has to say what it depends on.

## Two corrections of mine, recorded because the first was the load-bearing one

**1. I said purging the artifact makes the verification "unrepeatable". Too strong.** The artifact
**is** reproducible from the dump — by re-running the closure, i.e. a GPU job, not a file read.
**"Reproducible" is not "recoverable"**, and the distinction is the whole finding: the header is
honest about the first and silent about the second. The corrected form of the exposure is narrower
and more useful: **the window is bounded by the purge of *either* object, and after an artifact purge
re-verification costs a GPU re-run rather than a read. Increasingly expensive on a clock nobody is
watching — not unrepeatable.**

**2. I nearly mis-read the oracle.** `:46` says *"halves from the artifact's own
`dump_rows_a`/`dump_rows_b`, so no loader re-run"* — which is about not re-running the **loader**, and
does not mean the dump is unread. `:99` reads it. **A true comment about what a program avoids is not
a statement of what it consumes.**

## RESOLVED 2026-08-18 — the copy exists, and it is byte-identical

Filed with this pending. Measured since, and the branch resolves to **backed but undocumented**:

```
/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12_RECEIPT.json

scratch  9,897,374,636 B  2026-07-19 03:10:48.000000000
CFS      9,897,374,636 B  2026-07-19 03:10:48.000000000
sha256(CFS) = fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
```

**That digest is the pin** — `EXPECTED_INPUT_SHA`, the same value the Gate-5 launcher verifies and the
same one `CLM-012`'s row cites as *"the acceptance map pins the G2 dump `fa6b3463…`"*. So the copy is
not merely present at the right size and mtime; **it is the pinned artifact.** CFS is not purgeable.
The receipt was staged beside the payload, so whoever did this copied the pair rather than the bytes
alone.

**SCOPE, because a positive from a truncated search needs one.** My first search was **killed, not
completed** — reported as killed rather than allowed to stand as a null, which is this finding's own
lesson aimed at its author. The bounded re-run exited **124 (timed out at 90 s)** at `-maxdepth 4`.
That does not weaken the result: **one hit answers an existential.** It does mean **these are not
claimed to be the only copies**, and they are not. A truncated search supports *"a copy exists"* and
can never support *"this is where the copies are."*

**What resolves and what does not.** The *preservation* worry is discharged: the dump is safe, so the
`.gitignore`'s promise is true and its precondition is met. **The finding is unchanged**, because it
was never *"the dump might be purged"* — it was *"the promise does not say what it depends on."* The
remedy therefore shrinks rather than vanishing: **one clause naming the CFS path**, after which a
reader can check the claim instead of trusting it.

**And the chain result is untouched — it is still the class.** `git ls-files` at both hops returns a
receipt and no payload, so the enumeration's question stops at every hop exactly as before. **A CFS
copy that nobody has written down is not discoverable by asking *"is the backing artifact
tracked?"*** — it took a filesystem search to find, and the next lane will not run one. **Preserved
and findable are different properties, and only the first of them is now established.**

**Routed, not claimed:** the staging directory is named `minerva-shutdown-stage`, which reads like a
deliberate preservation exercise indexed nowhere locatable from the repo. If so there may be a
preserved population that `OI-130`'s enumeration cannot see — good news for its remediation, bad news
for its method. That is `OI-130`'s owner's item.

## Family

- `BEN-255` — a check evaluated on the wrong population. Here: an enumeration whose question cannot
  reach past the first hop.
- `BEN-258` — `cannot-fail` is a two-place predicate. Same move: a property asserted without the
  qualifier that makes it decidable.
- **`BEN-259`** — an exclusion justified by a reproducibility guarantee whose preconditions carry the
  same exposure as the thing excluded, **with a tracked receipt at every hop to stop the search.**
