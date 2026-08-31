# DECISION 2026-08-31 — the seven quarantine causes are graded against the STAMPED CANDIDATE,
# not against the adopted July artifact. X is retained.

**CITABLE FOR:** the ruling in §1, its authority in §0, and the measurements in §2 that this lane
verified independently. **NOT CITABLE FOR:** adoption of anything; discharge of any cause; a change to
`values.tex`; a change to the quarantine counts; any gate movement; permission to move, overwrite or
delete the July artifact; leg 6; or the M(ii) family. **Gate 2 remains FAIL. No scalar-5D covariance
is adopted. The counts stay CAND `1 of 7`, QUOTED `0 of 7`.**

## 0. Authority

Joseph, relayed by the personal-account producer session, on the ruling: **"Okay it sounds like the
correct ruling"** and **"Okay do that"**. On retention, in answer to his own question *"should we even
keep the July artifact still?"*, that session argued against deletion and he accepted, so **retention
is part of the ruling, not an inference from it**.

**CONFIRMED DIRECTLY before this record was written.** This lane put the whole ruling back to him in
its own words and he answered **"yes its my ruling"**. A relayed grant is hearsay and in this
repository authorization is itself an evidence artifact, so both the relay and the direct confirmation
are recorded. The framing below is the producer session's; the verification in §2 is this lane's.

## 1. THE RULING

> **The seven quarantine causes are graded against
> `stamped_bkgaware_meancentered_20260812.root`** — sha256 `4f168e83…`, CV variant `dbcd5359…`, job
> `56720356` — **NOT against the adopted July artifact X.**
>
> **X is RETAINED.** Not deleted, not moved, not overwritten.
>
> **The only disposition ever authorized for X is DEMOTION, and only after adoption**, in this order:
> grade the quarantine against the candidate → discharge what can be discharged → adopt → re-point
> `values.tex` → **only then** move X to a quarantine directory under the 2026-08-30 pattern (`mv -n`,
> a 0-line diff on both the sha256 set and the `(relpath, bytes, mtime, inode)` ledger, a receipt,
> nothing deleted). **Nothing about X moves before adoption.**

## 2. Why the subject can be chosen — verified rather than accepted

The producing session asked that its reasoning be checked rather than taken, because two of its
earlier framings on this subject were wrong. Every checkable claim holds.

**(a) The framework already makes discharge a (cause × artifact) property, so this is a sanctioned
move inside `CRITERIA-20260811`, not a workaround of it.** §0, verbatim: the quarantine paragraph is
*"a statement about a **class** of products, and a class has no construction — so there was no subject
for a criterion to be about. Every attempt to write 'what would discharge cause 1?' fails at the same
place: discharge for **which** matrix?"*

**(b) Against X the provenance leg is unsatisfiable IN PRINCIPLE, which is stronger than `§4.2`'s
"currently unsatisfiable from committed artifacts for causes 1–4".** Measured by this lane:

| fact | value | source |
|---|---|---|
| g2 input `unified_throw_cov_5d.root` mtime | **2026-07-13 02:15:41 −0700** | `stat` on the canonical cluster checkout |
| same file ctime | **2026-07-13 02:15:41 −0700** — *equal to mtime* | same |
| size | 2,677,168,123 B | same |
| `fixed_seed_null_norm` first enters git | **`07c18aee`, 2026-07-14 14:43:19 −0700** | `git log -S`, oldest hit |

**The artifact was written about 36.5 hours BEFORE the code whose keys would stamp it existed in git**,
and `ctime == mtime` rules out a later restore or copy that would have reset ctime. So no stamp for X
can ever be produced: the producing revision is unrecoverable and a re-run yields a different
artifact. **This is permanent for X, not a gap awaiting work.**

**(c) Against the candidate the same leg IS satisfiable.** It carries
`fixed_seed_null_norm_checked=1`, `joint_mean_shift_norm_checked=1`, `n_throws_checked=1`,
`upstream_n_throws=160`, and `centering_convention` / `uthrow_source` / `combined_source` as `TNamed`
— **it names its own upstream, which X does not.** `receipt_construction_contract_5d.json` records
X's adopted ROOTs as carrying those keys absent.

**(d) The standing counts already assume this split**, so the ruling ratifies existing bookkeeping
rather than changing it. `VALIDATION_LEDGER.md:728`, row `VL63`: *"DISCHARGED 2026-08-12 for the
footing-matched, stamp-verified candidate ONLY … still OPEN for the adopted 5D GBDT covariance."*

## 3. Why X is retained — four reasons, and the first is the repository's own guard

1. **A deliberate deletion would do exactly what an existing guard was built to prevent.**
   `PREDECLARE-20260811-bkgaware-footing-readopt.md:44` records that `adopt_unified_5d.py` defaults to
   the July product and opens it **`RECREATE`**, so *"taking the default would destroy a historical
   artifact"* — which is why all four arms passed `--out` explicitly.
2. **X is what `values.tex` quotes TODAY**, so it backs the current publication state.
3. **X is the subject of `OI-172` and of live ledger rows.**
4. **The candidate's whole justification is that it differs from X "by the flux fix alone", which is
   only checkable while both exist.** Deleting X would destroy the evidence for adopting its
   successor.

## 4. What this ruling does NOT do

`PREDECLARE-20260811:7` still governs: **"THIS ADOPTS NOTHING. The 2026-07-12 quarantine stands,
causes 1–6 are open, `values.tex` is untouched."** This decision **adopts nothing, discharges no
cause, moves no gate, and changes no count.** It redirects the SUBJECT of the discharge work and
nothing else.

## 5. The measured difference, attributed

The producing session's decomposition, performed before it read `PREDECLARE-20260811` and therefore
independent of the predeclaration's stated intent: the candidate totals **5.269625166386846e-38**
against X's **5.807716496958672e-38**, ratio **0.9073**. At throw level `sqrt_tr_unified` moves 0.996
while `sqrt_tr_block` moves 1.102, and `adopt_unified_5d.py:173` applies `hInflation_g` as a per-bin
unified/block sigma inflation, so the implied inflation falls **1.311 → 1.185**. The flux fix raised
the block sum, which reduced the inflation, which accounts for the whole −9.3%. Both `sqrt_tr_old`
values are byte-identical at **4.357790406860002e-38**, so the footing is matched as designed.

**This lane corroborated the three numbers against committed records rather than recomputing them**:
`4.357790406860002e-38` appears 41 times in the tree, the candidate's total 14 times, X's 12 times.
**The chain from flux fix to inflation to −9.3% is the producing session's measurement and is
attributed, not independently re-derived here.**

## 6. A CORRECTION that must not be inherited

The producing session twice told Joseph that X was *"known to be superseded"* and that its re-pointing
had been *"forgotten"*. **Both are wrong and it withdrew them.** `07c18aee`'s own subject is *"close
KNOWN_ISSUES #13 (bkgaware background) + **adopt corrected #14 covariances**"* — X was **deliberately
adopted** as the #13/#14 resolution with a stated verdict. And `PREDECLARE-20260811` shows the
non-re-pointing was deliberate and correct, because the quarantine gates adoption.

**Nobody erred.** Recorded here because a record that repeated the original framing would impute a
lapse to a decision that was sound, and this document exists partly to stop that.
