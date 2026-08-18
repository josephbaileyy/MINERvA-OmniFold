# CONCORDANCE — `unified_throw_cov.py` line citations across the gate-1 two-role seed split

**Lane B, 2026-08-18. Baseline `26e4e343` (pre-diff) → the diff's tree. Machine-derived; do not hand-edit.**

**WHY THIS EXISTS INSTEAD OF A CORRECTION PASS.** Item 5 of the gate-1 scope requires comparing the
set of `(file, cited-line)` pairs before and after, and *for every pair whose line moved, verify the new
line names the same code and correct the citation*. **Discharged as specified, the comparison says the
obligation cannot be fully met by correcting:**

| | |
|---|---|
| distinct cited lines of `unified_throw_cov.py` (baseline, `*.jsonl` excluded) | **50** |
| still naming the same code after the diff | **12** |
| ROTTED | **38** |
| citing files affected | **33** |
| of those, FROZEN by policy — append-only logs, archives, verifier transcripts, predeclarations | **12** |
| rotted lines resolvable to a UNIQUE new line by content | **24** |
| content now matching MULTIPLE lines (ambiguous) | **4** |
| content GONE from the file entirely | **10** |

**Twelve of the thirty-three citing files must not be edited at all** — `ND_OMNIFOLD_RUN_LOG.md` and both
`AUTONOMOUS_LOG_20260805.md` are append-only (`BEN-254`: one inserted line breaks 443 citations),
`*ARCHIVE*` are archives, `docs/orchestration/runs/*.txt` are verifier transcripts whose citations are
historical utterances, and `PREDECLAR*` bodies are frozen by construction. **A correction pass is
therefore not available for the majority of the affected surface, and 10 of the 38 have no new line to
point at because the cited code no longer exists.** This table is the recovery mechanism that works
anyway: a reader at a stale citation looks the old line up here and gets the content and its new home.

**AND IT IS THE HONEST FORM OF `BEN-249`'s CLAUSE.** *Cite the line and quote it* would have made 24 of
these self-repairing without this file. The 10 deleted lines it would NOT have saved — those are the
`BEN-249` §6a case, a citation asserting a BEHAVIOUR rather than naming a location.

## The mapping

**Full paths, and EVERY citer — no truncation.** Amendment 1 replaced a rendering that showed the
first three citers as basenames plus a count; see §Amendment 1.

| old | content at the baseline | new | every citing file |
|---|---|---|---|
| `:223` | `rng = np.random.default_rng(args.seed + gj)` | **LINE DELETED** | `VALIDATION_LEDGER.md`<br>`docs/orchestration/HANDOFF-20260817-1133Z.md`<br>`docs/orchestration/SCOPE-20260818-gate1-seed-separation-two-keys.md`<br>`docs/orchestration/notify_uthrow_regen.sh`<br>`nd-unfolding/AUTONOMOUS_LOG_20260805.md`<br>`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`<br>`nd-unfolding/validate_rescale_identity.py` |
| `:244` | `x = _xsec_for_weights(d, edges, wt_j, wr_j, wtd_j, args.iters, args.seed,` | **LINE DELETED** | `docs/orchestration/FINDINGS.md` |
| `:254` | `seed=np.int64(args.seed),` | **LINE DELETED** | `docs/orchestration/FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:255` | `flux_normalized=np.int64(1),` | AMBIGUOUS `:256`,`:288`,`:306` | `docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`<br>`nd-unfolding/AUTONOMOUS_LOG_20260805.md`<br>`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`<br>`nd-unfolding/sbatch_j28_adopt_5d.sh` |
| `:281` | `x = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed).ravel(or` | **LINE DELETED** | `docs/orchestration/COST-20260817-mii-seed-scan-derivation.md`<br>`docs/orchestration/FINDINGS.md` |
| `:297` | `args.iters, args.seed,` | **LINE DELETED** | `docs/orchestration/FINDINGS.md` |
| `:321` | `slabs = sorted(glob.glob(args.combine))` | `:324` | `docs/orchestration/FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md` |
| `:326` | `slab_seeds = set()` | `:329` | `docs/orchestration/FINDINGS.md` |
| `:328` | `for s in slabs:` | `:332` | `docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md` |
| `:330` | `if "seed" in z.files:` | **LINE DELETED** | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md`<br>`docs/orchestration/FINDINGS.md`<br>`docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md` |
| `:331` | `slab_seeds.add(int(z["seed"]))` | **LINE DELETED** | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md`<br>`docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md`<br>`docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md` |
| `:332` | `if not _flux_normalized(z):` | AMBIGUOUS `:338`,`:380` | `KNOWN_ISSUES-ARCHIVE-2026-08.md`<br>`docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260807T220756Z-repair5-transcript.txt`<br>`docs/orchestration/runs/standard-p4-verifier/20260809T075632Z-repair6-transcript.txt`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-judgement.txt`<br>`nd-unfolding/sbatch_j28_adopt_5d.sh` |
| `:355` | `C_uni, mean_shift = joint_throw_covariance(X, base)` | `:361` | `VALIDATION_LEDGER.md`<br>`docs/orchestration/FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`<br>`docs/orchestration/VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:368` | `for s in bslabs:` | `:374` | `docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md` |
| `:372` | `if not _flux_normalized(z):` | AMBIGUOUS `:338`,`:380` | `KNOWN_ISSUES-ARCHIVE-2026-08.md`<br>`docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260807T220756Z-repair5-transcript.txt`<br>`docs/orchestration/runs/standard-p4-verifier/20260809T075632Z-repair6-transcript.txt`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-judgement.txt`<br>`nd-unfolding/sbatch_j28_adopt_5d.sh` |
| `:400` | `C_block += mat_covariance(np.stack([knob_x[band]["0"], knob_x[band]["1"]]))` | `:408` | `VALIDATION_LEDGER.md`<br>`docs/orchestration/FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`<br>`docs/orchestration/VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:407` | `C_flux = mat_covariance(np.asarray([flux_x[u] for u in sorted(flux_x)]))` | `:415` | `VALIDATION_LEDGER.md`<br>`docs/orchestration/FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`<br>`docs/orchestration/VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:417` | `if slab_seeds and slab_seeds != {int(args.seed)}:` | **LINE DELETED** | `docs/orchestration/COST-20260817-mii-seed-scan-derivation.md`<br>`docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md`<br>`docs/orchestration/FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md`<br>`docs/orchestration/FINDINGS.md`<br>`docs/orchestration/INDEX-retracted-and-superseded-values.md`<br>`docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md`<br>`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` |
| `:419` | `f"--seed {args.seed}; refusing mixed-seed combine")` | **LINE DELETED** | `docs/orchestration/COST-20260817-mii-seed-scan-derivation.md`<br>`docs/orchestration/FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md`<br>`docs/orchestration/FINDINGS.md`<br>`docs/orchestration/INDEX-retracted-and-superseded-values.md`<br>`docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md` |
| `:424` | `raise SystemExit(` | AMBIGUOUS `:438`,`:445` | `nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md` |
| `:435` | `st_uni = float(np.sqrt(np.trace(C_uni)))` | `:455` | `docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md` |
| `:437` | `# Fixed-seed null: this must be exactly zero (within floating tolerance).` | `:457` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` |
| `:445` | `tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)` | `:465` | `docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md`<br>`docs/orchestration/FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`<br>`docs/orchestration/FINDINGS.md`<br>`docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md`<br>`nd-unfolding/receipt_candidate_stamps_5d.py`<br>`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` |
| `:447` | `if null_norm > tol:` | `:467` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` |
| `:449` | `"seed; the throws cannot be cleanly separated from C_ML "` | `:469` | `docs/orchestration/FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:451` | `"enforced separately below)")` | `:471` | `docs/orchestration/FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:479` | `ROOT.TParameter("double")("sqrt_tr_unified", st_uni).Write()` | `:499` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/FINDINGS-ARCHIVE-2026-08.md`<br>`docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt`<br>`nd-unfolding/receipt_candidate_stamps_5d.py`<br>`nd-unfolding/receipt_construction_contract_5d.py` |
| `:480` | `ROOT.TParameter("double")("sqrt_tr_block", st_block).Write()` | `:500` | `docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt` |
| `:481` | `ROOT.TParameter("double")("joint_mean_shift_norm", float(np.linalg.norm(mean` | `:501` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt` |
| `:482` | `# NULL-AS-ABSENT, closed 2026-08-11 (quarantine cause 4). 'fixed_seed_null_n` | `:502` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`<br>`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` |
| `:483` | `# written only when the check ran -- a number nobody measured must not be in` | `:503` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt`<br>`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` |
| `:484` | `# 'fixed_seed_null_checked' is now written UNCONDITIONALLY beside it. Withou` | `:504` | `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`<br>`docs/orchestration/FINDINGS-ARCHIVE-2026-08.md`<br>`docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`<br>`docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt`<br>`nd-unfolding/receipt_construction_contract_5d.py` |
| `:487` | `# zero. The flag makes "nobody checked" a readable state rather than an infe` | `:507` | `docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md` |
| `:489` | `ROOT.TParameter("int")("fixed_seed_null_checked", 1 if null_norm is not None` | `:509` | `nd-unfolding/receipt_candidate_stamps_5d.py` |
| `:491` | `ROOT.TParameter("double")("fixed_seed_null_norm", null_norm).Write()` | `:511` | `docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md` |
| `:498` | `print(f"[combine] wrote {args.out_root}")` | `:524` | `docs/orchestration/runs/standard-p4-verifier/20260810T012645Z-repair7-transcript.txt` |
| `:509` | `"fixed_seed_null_checked": null_norm is not None,` | `:535` | `docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md` |
| `:525` | `ap.add_argument("--seed", type=int, default=1000)` | **LINE DELETED** | `VALIDATION_LEDGER.md`<br>`docs/orchestration/COST-20260817-mii-seed-scan-derivation.md`<br>`docs/orchestration/EXTENT-20260817-2850-a100h-scope-and-missing-legs.md`<br>`docs/orchestration/PREDECLARATION-20260817-mii-seed-scan-cause-3.md`<br>`docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md` |

## Amendment 1 — what the enumeration COVERS, and a truncation that hid a receipt citer

**THE ENUMERATION'S SCOPE, stated because a sweep that does not name its own scope cannot be
checked at the point of use:**

    git grep -noE 'unified_throw_cov\.py:[0-9]+(-[0-9]+)?(,[0-9]+)*' 26e4e343 -- . ':!*.jsonl'

**COVERS every tracked path of every extension except `*.jsonl`** — so prose, `*.json` receipts,
`*.tsv`, `*.txt`, shell and Python are all in. **EXCLUDES `*.jsonl`** (5 verifier-transcript files, 12
occurrences) as historical utterances. **DOES NOT COVER**: citations that name the module without a
line, citations of the `unified_throw_cov_5d.py` wrapper's own lines, any untracked file, and any
citation whose spelling differs from the pattern — `BEN-235`'s family, and the pattern is exact,
which is what makes it narrow.

**THE TRUNCATION, and it is mine.** Lane A, via the mediator, reported that
`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` cites `:445` four times and was absent from this
file's citer list. **Measured: it was NOT absent from the enumeration — it is one of the 6 citers
recorded for `:445`. It was absent from the RENDERED TABLE, which printed the first three citers as
BASENAMES plus a count.** So the data was right and the document was not, in two ways at once: a
`head`-shaped truncation, and `basename` discarding the path that distinguishes two files.

**That is *never truncate a search you will draw a conclusion from* violated in the OUTPUT layer**,
which is the layer nobody checks because the query looked right. And it matters more here than in a
prose document, for the reason the mediator gives: **`tol_source` is an INGREDIENT
(`CONVENTION-receipt-ingredients.md`, `BEN-077`) — the operand that lets a reader check
`ratio_to_tol` against `tol` — and a committed JSON receipt cannot carry a *see the concordance*
annotation without changing what parsers read. A prose citer can still be fixed in place later; a
receipt citer has no other route, so this file's coverage is load-bearing for it and only for it.**

**`:445` maps to `:465`, and the mapping was correct throughout** — nothing about the receipt's
recoverability was ever wrong, only its visibility here. **The receipt itself is NOT corrected: it is
lane E's product and `tol_source` is a machine-read field.**

**The general form, which is this file's own worst failure mode: A CONCORDANCE WHOSE COMPLETENESS
CANNOT BE CHECKED FROM THE CONCORDANCE is in the family of checks retired today.** It is the discharge
for 12 uneditable files, so its coverage is exactly what nobody can verify at the point of use.
Amendment 1 makes it checkable: full paths, every citer, and the scope of the sweep printed above.
**Found only because lane A went into a receipt for unrelated reasons.**

## Ownership of the remaining correction

**Not done here, and named rather than left implicit.** Of the 21 editable citing files, this lane owns
only its own (`SCOPE-20260818-*`, `EXTENT-20260817-*`, `FINDING-20260817-a-seed-census-*`,
`FINDING-20260817-a-source-line-citation-*`, and its own `FINDINGS.md` rows). The rest are other lanes'
`CRITERIA-*`, `DETERMINATION-*`, `SCOREBOARD-*`, `COST-*`, `INDEX-*` and `VALIDATION_LEDGER.md` rows;
**editing another lane's row is what `BEN-381` forbids**, so those are notified, not rewritten. The
concordance makes each one a mechanical lookup rather than a re-derivation.

**Regenerate with:**

    git grep -noE 'unified_throw_cov\.py:[0-9]+(-[0-9]+)?(,[0-9]+)*' <ref> -- . ':!*.jsonl'

**The ref is part of the command** — a command over a mutable corpus is not a definition (`BEN-431`,
extended: publish the command AND the ref). The baseline above moved by 2 occurrences between being
measured and being published, because the document publishing it cited the lines it was counting.
