# Method declaration — lane D's `C_stat` cross-check, written before the build and before B's artifact exists

> ## ⚠ THE PRE-COMMITMENT IS VOID AS OF 2026-08-14. I NEVER BUILT, AND `C_stat` LANDED FIRST.
>
> This document's own condition, stated below and quoted verbatim: *"If that stops being true
> before I build, this file is void and I will say so rather than proceed as though it held."*
>
> **It stopped being true.** `docs/orchestration/state/gate5-cstat-n50/GATE5_CSTAT_N50.npz` was
> committed at **`87046fe`** ("Preserve the C_stat matrix itself in the tree, not only its
> receipt"). My two OI-120 jobs sat queued for ~7 h and the cross-check was sequenced behind
> them, so the artifact existed on `origin/main` before I had built anything.
>
> **What is lost.** Not the ability to build a cross-check — the ability to claim it was built
> blind. Any covariance I produce now is produced with the other artifact visible to me, which is
> exactly the tuning-toward-agreement exposure the mechanism existed to exclude. **Agreement would
> no longer be evidence of independence**, and the method below, which is otherwise unchanged and
> still sound, cannot supply that property retroactively.
>
> **What is not lost.** The method is still fully specified in advance of any build, so a
> cross-check run now would still be *pre-specified* even though it is no longer *pre-committed*.
> Those are different claims and only the weaker one survives. Whether it is worth building on
> those terms is Joseph's call, not mine to make quietly.
>
> **This banner exists because a message to one peer is not a record.** The condition triggered;
> the document that set it has to be the document that says so.

**STATUS: CONTINGENT. Nothing here is authorized yet.** `§4.F` of
[`COMPARATOR-PREDECLARATION-20260814-cstat.md`](COMPARATOR-PREDECLARATION-20260814-cstat.md) is with
Joseph. **If he declines, this file is a record of a build that did not happen and nothing else.** It
is written now because it is worthless written later.

## Why this file has to exist before the build

With one builder, a lane-D cross-check would make me builder *and* comparator — the self-verification
problem one level up, which is the thing I have spent this campaign filing findings about. Two
mechanisms make the comparison mean something, both agreed with the orchestrator:

1. **My artifact is produced and committed BEFORE B's exists or is visible to me**, so it cannot be
   tuned toward agreement.
2. **My method is declared before I build**, so I cannot reach agreement by choosing, after the fact,
   whichever construction happened to match.

**State of the world at writing, measured this turn rather than assumed:** no `C_stat` artifact exists
on `origin/main` from any lane, and the extraction family stands at **18 of 50** products, so B cannot
yet have built one — the `PASS` criterion requires 50 complete manifests. **The pre-commit mechanism is
intact.** If that stops being true before I build, this file is void and I will say so rather than
proceed as though it held.

## What I will read, and what I will not

**I will not read `nd-unfolding/pet/combine_cstat_bkgsub.py`.** It is existing committed prior art, not
B's build, so reading it breaks no constraint — but B's `REQUIREMENTS` cites it as the precedent for
this construction, so **if B builds on it, reading it would pre-load B's approach** and the
independence I am here to supply would be gone before I started. The distinction between *prior art*
and *the other builder's implementation* collapses when the second is derived from the first.

**I will work from C's spec and the replica products only.** Not from B's artifact, not from B's code,
not from the assemblers B cites.

## The method, fixed now

1. Enumerate `GATE5_REPLICA_XSEC.npz` under the family root. Record every path and its `sha256`.
   **Refuse to proceed on anything other than exactly 50** — a missing replica is an invalid manifest,
   not a 49-replica ensemble (`PREDECLARATION-20260813` branch `BLOCK`, adopted verbatim).
2. Load each `xsec`, ravel **C-order** to 285, stack to `X` of shape `(50, 285)`.
3. Centre on the **replica mean** — `Z = X - X.mean(axis=0)`.
4. `C = (Z.T @ Z) / 49`, i.e. **`dof = 49`**, matching the spec's `centering = "replica_mean"`.
5. Symmetrise explicitly and **record `max|C - Cᵀ|` before doing so**, as the spec requires and as I
   argued should be a required field.
6. **Derive my own reported mask** as the union over replicas of `xsec > 0`, and **do NOT adopt
   `C_syst`'s or B's.** This is deliberate: `C_stat` is a mask *consumer* in production, but a
   cross-check that adopts the mask under test cannot detect a mask error. Any difference between my
   mask and the adopted one is then a finding rather than something the method hides.
7. Emit the full contract: `(285,285)` `C_stat`, my `reported_mask`, the reduced
   `(n_reported, n_reported)` derived from both, `cv`, `layout_fingerprint`, `member_sha256`,
   `replica_ids`, `dof`, `centering`, `ravel_order`, `units`,
   `asymmetry_before_symmetrisation`, and this file's name as `method_declaration`.
8. **Commit and push the artifact.** Only then look at B's.

## What this will and will not be evidence of

Stated now so that a clean agreement cannot later be read as more than it is.

- **Weak evidence about the kernel.** Per `BEN-188`, `Xc.T @ Xc` and `np.einsum` agree *bit-for-bit*
  because both dispatch to the same BLAS. If B reached for the same arithmetic — and step 4 above is
  the obvious construction — then agreement on the covariance kernel is evidence about BLAS.
- **Meaningful evidence about everything above the kernel**: which 50 files were consumed, the
  centring, the mask, `dof`, the ravel order, the reduction. **That is where the bugs actually are**,
  because a spec pinning a decision is not a builder implementing it correctly.
- **No evidence at all about whether the replica products themselves are right.** Both of us read the
  same 50 files. `member_sha256` proves we read the same bytes; nothing here proves those bytes are a
  correct extraction.

**If B and I agree, the claim is "two independent assemblies of the same 50 products agree above the
kernel."** Not "`C_stat` is verified." I will write it that way in the receipt.

## The branch that costs me something, declared in advance

**If we disagree, the presumption is NOT that B is wrong.** I am a verifier writing assembly code for
the first time on this object, against a spec I did not author, and B owns the P5B assembly
conventions. **A disagreement is a finding about the pair, and the first hypothesis I will test is that
mine is the defective one.** Recorded here because that is easy to write now and hard to mean later.
