# FINDING 2026-08-18 — the evidence for an irreversible deletion must outlive the thing it verified

`BEN-490`. Episode: HPSS → CFS migration of `mnv-p3f-pet-fullevent-final`
(copy `57199158`, re-verify-and-delete `57214668`), receipt
[`RECEIPT-20260818-p3f-hpss-to-cfs-migration.md`](RECEIPT-20260818-p3f-hpss-to-cfs-migration.md),
open item `OI-131`.

## The verification was correct, and that is what makes this worth writing

Nothing about the migration's checking was weak:

- 240/240 objects matched **the md5s HPSS stored at write time** — an independent, pre-existing
  digest, not a hash recomputed from the copy. A copy checked against its own hash proves nothing
  about the transfer.
- The resume guard keyed on a post-verification marker, not on file existence (`BEN-023`).
- The re-verify ran **inside the deletion job**, so the last check preceded the first `hsi rm` by
  seconds instead of by the ~15 h that separated the copy from the decision to delete.
- Byte totals agreed exactly (1,134,998,230,283 on both sides), and the one 32,768 B discrepancy
  that surfaced was chased to the directory inode rather than waved off.

A reviewer auditing "was the migration verified?" would answer yes, correctly, and stop.

## The defect is about where the proof lived, not whether it existed

Every artifact establishing the above — the file manifest, the md5 manifest, the re-verify log,
both job scripts, both job logs — lived in
`/global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/`.

Three properties of that location, none individually alarming:

1. **The name reads as disposable.** `p3f-move-20260818/` is shaped like a working directory for
   a one-day task. Nothing marks it as the permanent record of anything.
2. **It is on the same filesystem as the surviving copy.** The proof and the artifact it vouches
   for share a failure domain. A CFS-level loss takes both.
3. **It is not in the repo**, so none of the repo's retention conventions, catalogues, or
   pre-commit checks apply to it. `MANIFEST.tsv` cannot classify a file it has never seen.

**And after the deletion the verification is unrepeatable in principle, not merely inconvenient.**
The independent operand — the tape copy carrying HPSS's stored digests — no longer exists. Before
the `hsi rm`, "was this copied correctly?" was a question anyone could re-answer from scratch.
After it, that question has exactly one remaining answer anywhere in the world: a manifest in a
directory named like scratch.

## Who found it, and why that matters

Not the lane that ran the migration. It was raised by a **different session** (the mediator, at
`ffa32007`) reading the commit that recorded the deletion, and flagged in one line: *"p3f-move-20260818/
is the sole record that the verification happened once the source is gone, and it reads as a
disposable working directory."*

This is the `BEN-077` discovery shape — the defect surfaced from a reader reconstructing the claim
rather than from the executor re-checking their own work — and it generalises: **the executing lane
is structurally the worst-placed party to notice that its evidence is impermanent**, because to that
lane the evidence is right there, in the shell it is still sitting in.

## The rule

> When a verification's inputs are about to be destroyed, the verification record is promoted to a
> committed artifact **in the same commit that authorizes the destruction** — not after it, and not
> in a follow-up item.

"Not after it" is the operative half. A follow-up is a promise made by a session that may not exist
tomorrow, about a directory whose name invites cleanup.

### Distinct from its two nearest neighbours

- **`BEN-077`** (every derived quantity ships its ingredients) is about a receipt's *contents*.
  This is about a receipt's *survival*. A perfectly-ingredient-ed receipt on a doomed filesystem
  fails this and passes that.
- **`BEN-023`** (validate completeness, not existence) guards *the copy*. This guards *the proof of
  the copy*. Both were satisfied here; only one was enough.

## Second-order instance in the same episode: the promotion silently half-failed

Committing the evidence, `git add` on the directory took the manifests and **silently skipped both
job logs** — `.gitignore:13` ignores `*.out` repo-wide, and the two Slurm logs are the only files
recording the deletion actually issuing. No error; the files simply were not staged. They are
committed as `*.log.txt`.

So the rule needs its own check: **the promotion must be verified to have landed**, because its
failure mode is silence. `git status --porcelain` after the `add`, or `git show --stat` after the
commit, is the whole cost.

## Third-order instance: the quota number nobody would have re-checked

`hpssquota` read **265.1% one second after the last `hsi rm`, and 265.1% again 71 s later**. HPSS
quota accounting is lazy. The predicted post-accounting figure is 58.6%
(1,357.22 GiB − 1,057.02 GiB = 300.17 GiB of a 512 GiB quota).

Reporting 58.6% as achieved would have been `BEN-323`'s declared-rendered-as-observed error, on a
number with no natural auditor — the recipient (a PI who asked why HPSS rather than CFS) has no way
to check it, and the reporting session had every reason to believe it. The empty directory listing
is the evidence the deletion took; the quota figure is a **prediction** until an `hpssquota` line
shows it, and `OI-131`(b) holds that open.

Related: the lazy-block-accounting rule (8) in `nd-unfolding/AUTONOMOUS_LOG_20260805.md`, filed for
CFS and true of HPSS for the same reason.
