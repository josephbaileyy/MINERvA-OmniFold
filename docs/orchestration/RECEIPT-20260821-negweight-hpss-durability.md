# Receipt — negweight durability step: 247 historical diagnostic ROOTs preserved to HPSS (2026-08-21)

**Result: PASS.** The 247 ROOT products backing the twelve real-data/production `\nw*` values are on
tape, digest-verified server-side, `hashverify`-confirmed by a full read off tape, and — the part a
`hashverify` cannot supply — **restored end-to-end and proven usable: all 247 files recovered,
digest-matched, and opened by ROOT (6154 keys, 0 unusable).** The recovery route is committed and
power-tested in the failing direction.

**These products are HISTORICAL DIAGNOSTIC EVIDENCE.** Preserving them does not make negative-weight
injection a supported current production path, does not revive the archived pre-freeze arm, and
changes no default. The headline 2D path is and remains the binned per-reco-bin purity down-weight.

**Authorization:** Joseph's negweight durability ruling, 2026-08-21 — preserve to HPSS, do **not**
git-track the ROOT population, do **not** rerun the study. Scope is the twelve real-data/production
values only; the four synthetic-toy values were already attested by
`receipts/RECEIPT-negweight-toy-20260821.json` and are ungated.

**This receipt does not by itself ungate anything.** It supplies the durability the twelve were
waiting on. The ungating lands separately, after this record is in a commit.

Machine-readable companion: `state/negweight-hpss-durability-20260821.json`
(sha256 `826f68e7f0e720500ab759774ba81615228d2946bba9d728399f185f85ae05fe`).
Raw evidence: `state/negweight-hpss-20260821/` (see its `README.md`).

---

## 1. What ran

| field | value |
|---|---|
| host | `login34` (Perlmutter), interactive — hsi authenticates fine from a login node here |
| preservation script | `2d-unfolding/HANDOFF_bkg_negweight/hpss_preserve_negweight.sh` |
| recovery script | `2d-unfolding/HANDOFF_bkg_negweight/hpss_recover_negweight.sh`, sha256 `e989051b7ff95bc0620f253e35ab5b8adf613d26c1adcdb403bad48e4b3bd970` |
| manifest builder | `2d-unfolding/HANDOFF_bkg_negweight/build_negweight_hpss_manifest.py` |
| HPSS archive | `mnv-negweight-historical-20260821` — 5 objects, 29,144,842 B = 27.79 MiB |
| put + verify | `2026-08-21T21:43:36Z` → `21:43:48Z` |
| migrate + residency | `21:43:48Z` → `21:48:50Z` |
| `hashverify -R` | rc **0** recorded unpiped, 5/5 `(md5) OK` |
| recovery route | `21:58:48Z` → `21:58:58Z`, **10 s**, exit **0** |
| work dir | `/pscratch/sd/j/josephrb/negweight-durability-20260821/` |

Inside the standing under-12 h approval; launched, not asked. No compute beyond hsi transfers and
one ROOT-open pass over 13.5 MiB.

**Executed copy = committed copy.** Both scripts were staged to the work directory and their sha256
compared against the local repo copies before running; both matched, and both were parsed on the
target interpreter (`GNU bash 4.4.23`, not this Mac's 3.2).

---

## 2. Scope, stated as a set and fail-closed

| family | count | HPSS object |
|---|---|---|
| `2d-unfolding/HANDOFF_bkg_negweight/runs/*.root` | 8 | `negweight_runs_8.tar` |
| `2d-unfolding/uq/negweight_boot/*.root` | 51 | `negweight_boot_51.tar` |
| `2d-unfolding/uq/negweight_uni/*.root` | 188 | `negweight_uni_188.tar` |
| **ruled total** | **247** | 13.53 MiB, largest member 56,659 B |
| beside-scope sidecars | 29 | `negweight_sidecars.tar` |
| self-describing label | 1 | `LABEL.txt` |

The list is **derived from the filesystem, never hardcoded**, and the counts are a fail-closed
precondition: if a glob returns anything but 8/51/188 the job refuses rather than archiving a subset
that a count would later read as complete.

**The products were single-copy on purgeable scratch, and that is measured rather than assumed.**
`/global/homes/j/josephrb/MINERvA-OmniFold` is a **symlink** to
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` (`readlink -f`), so the home-looking path and the scratch
path are one tree — there was no second copy anywhere. pscratch read **15.99/20.00 TiB = 79.9%** the
same day.

### Why four tars and not 247 `hsi put` calls

13.53 MiB across 247 files with a 56 KB largest member is the one shape HPSS is worst at, and
NERSC's guidance is to aggregate below ~100 MB. It also made the recovery test genuinely end-to-end:
a `hashverify` over a tar reads every byte of every member, and extraction proves the members come
back as files. Per-file sha256 **and** md5 for all 247 are in the manifest, so any single member can
still be checked independently after recovery without trusting a tar as a unit.

HPSS confirmed the choice: all five objects share **one Object ID**
(`000186a4-04-00000001-01eea03634ef0e70-3f1d`) at positions 12877–12881 on PV `AB038000` — HPSS
aggregated them into a single tape object.

---

## 3. Quota — measured before, not assumed

`hpssquota -u josephrb` (**not** `hsi`; `hsi ls -lRD` sizes an archive, not an allocation), read at
`21:43:30Z` immediately before the put:

```
josephrb usage on HPSS charged to m3246 |  300.17GiB |   512.00GiB |  58.6%
pscratch                                |   15.99TiB |    20.00TiB |  79.9%
```

Headroom **211.83 GiB**; the 27.79 MiB payload is **0.013%** of it. The quota was never the
constraint, but it was read rather than recalled.

Read again at `21:51:04Z`: **unchanged at 300.17 GiB / 58.6%.** That is expected and is not a failed
write. 27.79 MiB is 0.027 GiB — below the instrument's 0.01 GiB display resolution, and HPSS
accounting does not reflect small changes promptly (`OI-131` measured this same instrument reading
265.1% one second after a large delete). **The archive's own `hsi ls -lRD` byte count, not the quota
line, is the authoritative size of what was written.**

---

## 4. Tape residency — and a just-put object is NOT on tape

This is the trap that would have made a false receipt, so it is recorded as a measurement in both
directions.

**Before `migrate`, all five objects read zero bytes at the tape level:**

```
-rw-r-----  josephrb  josephrb  4  112498  DISK  460800  Aug 21 14:43  negweight_runs_8.tar
 Level   Count  Width  Bytes at Level
 1 (tape)   0       1                     (no data at this level)
```

HPSS writes into a disk cache and migrates on its own schedule. **The mode column's `DISK` is the
class-of-service name, not a residency**; residency is the `Bytes at Level` table. An `ls -V` taken
straight after a `put` shows exactly the above, and reporting it as preservation would have been
false. So `hsi migrate -R` is explicit (rc 0) and residency is read *after* it.

**After `migrate`, all five carry their full byte count on tape:**

```
 1 (tape)   1       1  10946560
  VV[ 0]: Object ID: 000186a4-04-00000001-01eea03634ef0e70-3f1d
  Pos: 12877+0   PV List: AB038000
```

### The residency instrument is shown able to fail

A check only ever run against tape-resident objects has not been shown able to report otherwise. So
a throwaway object was put and read immediately, in the same minute, from the same instrument
(`state/negweight-hpss-20260821/residency_negative_control.txt`):

- freshly-put object → `1 (tape) 0 … (no data at this level)` ✔ reports zero
- archive object after migrate → `1 (tape) 1 1 460800`, PV `AB038000` ✔ reports full count

---

## 5. `hashverify` — every byte read off tape

```
hsi -q "hashverify -R mnv-negweight-historical-20260821"     rc 0 (captured unpiped)
5 of 5 objects (md5) OK
```

`hashverify` **recomputes** the digest from the data, so it read all 29,144,842 bytes off tape. It is
not a metadata read. `-A` was **not** used: it means *auto-schedule retrievals*, not *all*, and on a
directory it warns `is a directory - ignored` and exits 0.

`TimeLastRead` on all five objects is `2026-08-21 14:48:50` local = `21:48:50Z` — inside the verify
window and after migration, so the recompute read the tape-resident copy.

### Coverage as a path-set diff, with a floor

`verified.paths` (from `hashverify`) vs `hashed.paths` (from `hashlist -R`), after normalising
`hashverify`'s absolute `/home/j/josephrb/…` against `hashlist`'s archive-relative output:

```
COVERAGE_EXACT verified=5 hashed=5 sets identical      diff rc 0, no output
```

Both sides must hold ≥ 5 paths before the diff is allowed to mean anything — see §8a for why that
floor is not decoration.

---

## 6. The tested recovery route — the half `hashverify` cannot supply

`RECEIPT-20260820-oi50-hashverify.md` §5 states the gap about itself: *"no object was restored and
re-read end-to-end into a usable file."* `hashverify` recomputes **in place** on HPSS. This closes it.

`hpss_recover_negweight.sh <manifest> <fresh-dest>`, run against the exact committed manifest:

| step | check | result |
|---|---|---|
| 1 | `hsi get` every object into a **fresh** destination | 5/5 retrieved |
| 2 | retrieved object sha256 + size vs the manifest | rc 0, 5/5, 0 bad |
| 3 | extract | rc 0 |
| 4 | **every** member's sha256 + size vs the manifest | 247/247 matched, 0 bad |
| 5 | path-set diff, **both directions** | `manifest_not_recovered=0`, `recovered_unexplained=0`, `recovered_beside_scope=30` |
| 6 | **usability**: open every recovered ROOT, read its keys | `root_files_opened=247 unusable=0 total_keys=6154` |

Step 5 is a set difference, not a count: 247 of something is not 247 of the right thing, so both
directions are reported and both are empty. Step 6 exists because byte-identity to a digest taken off
pscratch would inherit any corruption the original already carried — zombie, `kRecovered` and
zero-key files all count as failures. The destination must be fresh: extracting over an existing tree
lets a file that was already there pass as one the run recovered.

### The route is power-tested in the failing direction

`state/negweight-hpss-20260821/recovery/recovery_negative_controls.txt`:

| control | expected | got |
|---|---|---|
| (a) one hex digit changed in an `objects[].sha256` | fail at step 2 | **exit 3**, names the object |
| (b) one hex digit changed in a `ruled_products[].sha256` | fail at step 4 | **exit 4**, prints want vs got |
| (c) non-empty destination | refuse | **exit 2** |
| (d) manifest listing zero objects | refuse | **exit 2** |
| positive arm, re-run after the repair below | pass | **exit 0**, 247/247, 6154 keys |

### Manifest chaining, stated so it is not circular

The route necessarily ran before the `recovery` block describing it existed, so it consumed an
earlier build, sha256 `40e9aa707ec4cbf584f8ca2682462c33e24e16915feedeb4294d8e773e3aaa86`. Saying
"the difference does not matter" would be an assertion, so the invariant is measured instead.

The route reads exactly four fields — `hpss_dir`, `objects[]`, `ruled_products[]`,
`sidecar_products[]`. Hashed as a canonical subtree, those four are **byte-identical** in the
consumed build and in the committed one:

```
consumed 40e9aa70…  route-relevant subtree sha256 d725726ffab2a23e12cf7feb166ee9d0fb52fe35729a25105157f9c139b49311
committed          route-relevant subtree sha256 d725726ffab2a23e12cf7feb166ee9d0fb52fe35729a25105157f9c139b49311
```

So the whole-file digests differ only in fields the route never opens. This is the non-circular
anchor: the committed manifest's own `recovery` block cannot be evidence for itself, but the subtree
identity can be recomputed by anyone from the two files.

---

## 7. Provenance — and the frozen record's job list is a launch plan, not a record

The manifest carries the producing commit and the per-file digests the ruling asked for. Two things
came out of measuring it that the existing records get wrong.

### 7a. The producer was UNCOMMITTED when these ran

`2d-unfolding/unfold_2d_omnifold_unbinned.py`, sha256
`8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e`, git blob `9b43a07a`, first
committed at **`cf8a4a67`** ("negweight background subtraction: drivers, sbatch, validation record",
`2026-07-11T06:46:24-0700`). No commit touches the file between `cf8a4a67` and `main`, and the
on-disk file on **both** the local and the cluster checkout hashes to that value — so the file that
would execute and the file cited here are the same bytes.

**But `cf8a4a67` is the first commit CONTAINING the producer, not the HEAD at run time.** Every one
of the 247 products was written between `2026-07-07T19:33:04` and `2026-07-11T05:21:45` PDT —
`cf8a4a67` landed **1 h 24 m after the last one**. The code that ran was uncommitted working-tree
code and no run recorded its own HEAD.

What corroborates the identity is a version-distinct message string, not a digest: the run logs print
`[INFO] bkg-mode=purity: binned per-reco-bin purity down-weight (default, headline path).`, which is
the concatenated literal at `unfold_2d_omnifold_unbinned.py:1501-1502`. **That is corroboration, not
proof of byte identity, and neither this receipt nor the manifest claims more.**

Also: `sbatch_unfold_2d_MEFHC_5iter_universes_full_negweight.sh` and `sbatch_uni_CV_negweight.sh`
were both modified at `069c3b84` (2026-08-01), after these products existed. **The launcher versions
at `main` are not the versions that ran.**

### 7b. Three of the jobids the frozen state record credits produced NOTHING

`sacct` over 2026-07-07…07-12, read 2026-08-21 (`state/negweight-hpss-20260821/sacct_producers.txt`,
`provenance_summary.txt`):

| record's claim | measured |
|---|---|
| `bkg_negweight_state.md:507` — array `55668087` → `uq/negweight_boot/` | 11 tasks **FAILED** in 4–19 s; tasks 12–50 **CANCELLED** |
| `:503` — array `55668380` → `uq/negweight_uni/` | **CANCELLED**, never started |
| `:505` — `55668400` → the universe CV | **CANCELLED**, never started |

**Do not cite any of those three as the source of any product here.** What actually ran:

- **bootstrap replicas** — 50 separate COMPLETED `unfold_MEFHC_boot_nw` submissions, `55702331`…`55786530`, `2026-07-08T20:46:42`…`2026-07-10T22:11:31`, after **twelve** failed attempts. The window matches the 50 boot ROOT mtimes exactly.
- **universe replicas** — 400 COMPLETED `unfold_MEFHC_uni_nw` submissions, `55677842`…`55792262`, which produced **187 distinct outputs**: re-submissions overwrote filenames, so **per-file attribution is not recoverable from `sacct`**.
- **universe CV** — `55677844` (`unfold_uni_nw_CV`), End `2026-07-08T11:18:34`, matching the CV file's mtime `11:18:33` to one second.
- **the two covariance rollups were not produced by a batch job at all.** Both `nw_cov_analysis` jobs failed or were cancelled (`55677847` FAILED after 8 s; `55795507` CANCELLED at `05:21:03`). `uq_cov_negweight_boot.root` is stamped `05:21:45` and `rollup/uq_universe_covariance.root` `05:22:08` — 42 s and 65 s after that cancellation — inside interactive allocation `55795538` (`claude-hold`, TIMEOUT). Same interactive pattern as the seed-1 pair in `55665504`.

The general shape: **the state record's job list is what was submitted, and it was read as what ran.**
The two objects most load-bearing for `\nwSystRatio` and `\nwStatRatio` have the weakest provenance
in the set, because they were made by hand in a hold allocation.

### 7c. What no artifact records

No product carries a run-time git HEAD, a config hash, or a producing jobid. The only completion
marker in the whole set is `uq/negweight_uni/2d_xsec_MEFHC_5iter_lgbm_nw_uni_CV.root.done`, and it is
a **2026-08-04 backfill** (job `56322135`, `"ADOPTED: backfill, validator=root"`), not a record
written by the producing run. **This absence is the `OI-130` defect itself. The archive fixes
durability, not attribution** — and no future run can fix attribution for this family.

---

## 8. Three corrections, all mine, all found by a control rather than by review

### 8a. A coverage diff that could not fail

The first coverage step parsed `hashlist` with `$2=="(md5)"`. The real field is a bare `md5` — the
`(md5)` form is `hashverify`'s. That emptied one side of the comparison, **and an empty-set-vs-empty-set
diff is EQUAL.** The step failed loudly only because `set -e` caught the non-zero `diff`; had the
parse been wrong in the other order it would have reported perfect coverage over nothing. Fixed
(`$2=="md5"`, and `hashverify`'s trailing colon stripped), and a **non-empty floor on both sides** was
added so the diff alone is not the check. Both formats are now recorded in the script's comment,
measured rather than assumed.

### 8b. An idempotent re-run destroyed its own earlier evidence

The script was run twice (the second time with 8a's fix). The second run **re-executed the residency
block after the first had already migrated, overwriting `residency_before_migrate.txt` with a
post-migration reading under a "before" name.** The artifact is kept and renamed
`residency_before_migrate.CLOBBERED-SEE-README.txt` rather than deleted, because a deleted artifact
leaves no trace of the hazard. The pre-migration state is instead evidenced by the live negative
control in §4, which is the stronger form. The script now writes run-stamped residency filenames.

### 8c. The recovery route failed closed but silently

Found by the negative controls, not by reading the code: with `set -e` active, a checker's own
non-zero status aborted the script **before** the rc was written and **before** the diagnostic
printed. A real digest mismatch surfaced as a bare `exit 1` with an empty step file — no failing path
named. Repaired (`set +e` around each checker, rc captured, then read), controls re-run: distinct
exits 3 / 4 / 2 / 2 with the failing object or path named in each.

### 8d. A fourth, caught at staging: `.gitignore` would have dropped the tape-read evidence

`.gitignore:15` is a blanket `*.log`. A plain `git add` of the evidence directory **silently skips**
`hashverify.log` — so this receipt would have cited, as its proof that 5 of 5 objects read `(md5) OK`
off tape, a file git was not carrying. `git add` says nothing when it skips an ignored path.

`verify_receipt_artifacts.py` exists for exactly this defect and **does not cover it**: its rule is
scoped to binary extensions (`.root`, `.npz`, `.h5`, …) under `docs/orchestration/state/`, so a
`.log` walks past. Found by running `git check-ignore` over the directory before staging rather than
by trusting `git add`'s silence.

The three affected files are **renamed** to `.log.txt`, not force-added: `git add -f` fights the
ignore rule and leaves the next lane to rediscover the trap. Bytes unchanged, sha256 recorded in the
evidence directory's `README.md`. Worth someone's judgement separately: whether
`verify_receipt_artifacts.py`'s extension list should include text-log extensions, since a receipt's
evidence is more often a log than an array.

### 8e. Three recovery counts shipped as `-1` in the first committed manifest

Caught by re-reading the committed record rather than the builder. The step-4/5 summary puts three
keys on ONE line (`ruled_members_in_manifest=247 recovered_and_matched=247 bad=0`) while the rest sit
on their own, and the parse was anchored `^(\w+)=(\d+)$` — so it matched only the single-key lines
and `recovered_and_matched`, `ruled_members_in_manifest` and `bad` all defaulted to the sentinel
`-1`. The measured values were in the committed evidence the whole time; only the derived record was
wrong.

`-1` is at least visibly absurd rather than plausibly wrong, which is why it was caught. Fixed by
dropping the anchors and, more importantly, **replacing every `.get(key, -1)` with `m45[key]` plus an
explicit presence assertion**, so a future format change fails loudly instead of silently reporting a
sentinel. Same treatment applied to the step-6 counts.

**The generalisation, since this is five for five:** every one of these was a *reporting* defect in
a check that was substantively right. None of them would have changed the verdict, and none of them
would have been visible from a passing run. The one that would have done real damage is 8d, and it
was caught by asking an instrument (`git check-ignore`) rather than by reading the code. The common
root is a **format assumed instead of measured** — `hashlist`'s field layout, a filename's
uniqueness across runs, a checker's exit path, `git add`'s silence, a summary line's key-per-line
shape. In every case the substantive measurement was right and the thing that carried it was wrong,
which is the failure mode a receipt is least able to detect about itself.

---

## 9. What this supports, and what it does not

**Supports.** The 247 products backing the twelve real-data/production `\nw*` values exist off
purgeable storage, on tape, verified by a full-byte read, with per-file sha256 and md5 committed, and
with a **tested, committed, power-tested recovery route**. The durability condition the twelve were
gated on is met.

**Does not support:**

- **Any claim that the negative-weight arm is a supported production path.** It is not, nothing here
  makes it one, and no default moved. The `LABEL.txt` inside the archive says so, so an operator who
  finds the tape copy without the repo reads the same caveat.
- **A revival of the archived pre-freeze arm**, or authorization to run it.
- **Any of the twelve values being re-derived.** Nothing was recomputed. This is durability, not
  re-derivation, and the ruling said so.
- **Either covariance RATIO being reproducible from this archive.** Both are negweight/purity and
  only the negweight side is here — `\nwStatRatio`'s purity operand is a matched 50-seed subset of
  the 300 adopted purity replicas at `uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root`, and `\nwSystRatio`'s
  is the corresponding purity universe set. **The numerator is preserved; the ratio is not
  reproducible from this archive alone.**
- **Attribution.** See §7c.
- **A permanent guarantee.** This is a point-in-time verify plus a point-in-time restore. The tape
  copy is **single-copy**, like the rest of this allocation.
- **git-tracking anything.** `.gitignore:2`'s blanket `*.root` is untouched, per the ruling.

---

## 10. Raised, not taken

1. **The ruled 51 includes its rollup covariance; the ruled 188 excludes the equivalent one.**
   `uq_cov_negweight_boot.root` sits directly in `negweight_boot/` so it is one of the 51.
   `rollup/uq_universe_covariance.root` — the product `\nwSystRatio`'s two sqrt-trace operands
   (`2.9828e-39` / `3.0242e-39`) were read from — sits in a subdirectory, so it is not one of the 188.
   **That asymmetry follows directory layout, not intent.** Both are preserved either way (the
   universe covariance is in the sidecar tar), but whether it belongs in the *ruled* set is Joseph's
   call, and the ruled counts would become 8/51/189 if so.
2. **The 29 sidecars are archived beside-scope and that was a judgement.** Dropping them would have
   left the ruled products without the witnesses `values.tex` cites by name —
   `ia_purity_seed1.log`, `ia_negweight_seed1.log` and the sbatch `.out` files carrying the printed
   totals. They are in their own object under their own name so the two sets cannot be conflated.
   If the ruling meant the ROOTs alone, the sidecar object can be deleted without touching the 247.
3. **No `RUNS.tsv` row exists for any of the 2026-07 producing jobs**, which is half of what
   `values.tex` complains about. §7b now supplies the measured facts to write them from, and it is
   cheap — but writing ~10 historical rows was outside this step and is left for whoever owns
   `RUNS.tsv` provenance.
4. **`values.tex`'s claim that "`hsi` cannot authenticate non-interactively from this node" is stale.**
   `hsi` authenticated from `login34` on the first try. That sentence is why the file recorded HPSS
   coverage as unconfirmed; it is confirmed now.
5. **The purity-side counterpart of this archive does not exist.** Item 3 of §9 is the reason. If
   either ratio is ever to be re-derived rather than quoted, the purity replicas need the same
   treatment, and they are a much larger set.
