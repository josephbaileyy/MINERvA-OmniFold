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

| old | content at the baseline | new | citing files |
|---|---|---|---|
| `:223` | `rng = np.random.default_rng(args.seed + gj)` | **LINE DELETED** | `VALIDATION_LEDGER.md`, `HANDOFF-20260817-1133Z.md`, `SCOPE-20260818-gate1-seed-separation-two-keys.md` +4 |
| `:244` | `x = _xsec_for_weights(d, edges, wt_j, wr_j, wtd_j, args.iters, args.seed,` | **LINE DELETED** | `FINDINGS.md` |
| `:254` | `seed=np.int64(args.seed),` | **LINE DELETED** | `FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:255` | `flux_normalized=np.int64(1),` | AMBIGUOUS `:256`,`:288`,`:306` | `PLAN-20260806-niter3-budget-and-J28-reroll.md`, `AUTONOMOUS_LOG_20260805.md`, `ND_OMNIFOLD_RUN_LOG.md` +1 |
| `:281` | `x = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed).ravel(or` | **LINE DELETED** | `COST-20260817-mii-seed-scan-derivation.md`, `FINDINGS.md` |
| `:297` | `args.iters, args.seed,` | **LINE DELETED** | `FINDINGS.md` |
| `:321` | `slabs = sorted(glob.glob(args.combine))` | `:324` | `FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md` |
| `:326` | `slab_seeds = set()` | `:329` | `FINDINGS.md` |
| `:328` | `for s in slabs:` | `:332` | `PREDECLARATION-20260817-mii-seed-scan-cause-3.md` |
| `:330` | `if "seed" in z.files:` | **LINE DELETED** | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `DETERMINATION-20260817-causes-3-4-provenance-measured.md`, `FINDINGS.md` +1 |
| `:331` | `slab_seeds.add(int(z["seed"]))` | **LINE DELETED** | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `DETERMINATION-20260817-causes-3-4-provenance-measured.md`, `PREDECLARATION-20260817-mii-seed-scan-cause-3.md` +1 |
| `:332` | `if not _flux_normalized(z):` | AMBIGUOUS `:338`,`:380` | `KNOWN_ISSUES-ARCHIVE-2026-08.md`, `PLAN-20260806-niter3-budget-and-J28-reroll.md`, `20260807T220756Z-repair5-transcript.txt` +3 |
| `:355` | `C_uni, mean_shift = joint_throw_covariance(X, base)` | `:361` | `VALIDATION_LEDGER.md`, `FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`, `VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:368` | `for s in bslabs:` | `:374` | `PREDECLARATION-20260817-mii-seed-scan-cause-3.md` |
| `:372` | `if not _flux_normalized(z):` | AMBIGUOUS `:338`,`:380` | `KNOWN_ISSUES-ARCHIVE-2026-08.md`, `PLAN-20260806-niter3-budget-and-J28-reroll.md`, `20260807T220756Z-repair5-transcript.txt` +3 |
| `:400` | `C_block += mat_covariance(np.stack([knob_x[band]["0"], knob_x[band]["1"]]))` | `:408` | `VALIDATION_LEDGER.md`, `FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`, `VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:407` | `C_flux = mat_covariance(np.asarray([flux_x[u] for u in sorted(flux_x)]))` | `:415` | `VALIDATION_LEDGER.md`, `FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`, `VALIDATION_LEDGER-VL-MAP-20260812.json` |
| `:417` | `if slab_seeds and slab_seeds != {int(args.seed)}:` | **LINE DELETED** | `COST-20260817-mii-seed-scan-derivation.md`, `DETERMINATION-20260817-causes-3-4-provenance-measured.md`, `FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md` +4 |
| `:419` | `f"--seed {args.seed}; refusing mixed-seed combine")` | **LINE DELETED** | `COST-20260817-mii-seed-scan-derivation.md`, `FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md`, `FINDINGS.md` +2 |
| `:424` | `raise SystemExit(` | AMBIGUOUS `:438`,`:445` | `AUTONOMOUS_LOG_20260805.md` |
| `:435` | `st_uni = float(np.sqrt(np.trace(C_uni)))` | `:455` | `DETERMINATION-20260817-causes-3-4-provenance-measured.md` |
| `:437` | `# Fixed-seed null: this must be exactly zero (within floating tolerance).` | `:457` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` |
| `:445` | `tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)` | `:465` | `DETERMINATION-20260817-causes-3-4-provenance-measured.md`, `FINDING-20260817-a-source-line-citation-has-no-immutable-handle.md`, `FINDINGS.md` +3 |
| `:447` | `if null_norm > tol:` | `:467` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` |
| `:449` | `"seed; the throws cannot be cleanly separated from C_ML "` | `:469` | `FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:451` | `"enforced separately below)")` | `:471` | `FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` |
| `:479` | `ROOT.TParameter("double")("sqrt_tr_unified", st_uni).Write()` | `:499` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `FINDINGS-ARCHIVE-2026-08.md`, `PREDECLARE-20260811-construction-contract-receipt.md` +3 |
| `:480` | `ROOT.TParameter("double")("sqrt_tr_block", st_block).Write()` | `:500` | `20260810T012645Z-repair7-transcript.txt` |
| `:481` | `ROOT.TParameter("double")("joint_mean_shift_norm", float(np.linalg.norm(mean` | `:501` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `20260810T012645Z-repair7-transcript.txt` |
| `:482` | `# NULL-AS-ABSENT, closed 2026-08-11 (quarantine cause 4). 'fixed_seed_null_n` | `:502` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `PREDECLARE-20260811-construction-contract-receipt.md`, `ND_OMNIFOLD_RUN_LOG.md` |
| `:483` | `# written only when the check ran -- a number nobody measured must not be in` | `:503` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `PREDECLARE-20260811-construction-contract-receipt.md`, `20260810T012645Z-repair7-transcript.txt` +1 |
| `:484` | `# 'fixed_seed_null_checked' is now written UNCONDITIONALLY beside it. Withou` | `:504` | `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`, `FINDINGS-ARCHIVE-2026-08.md`, `PREDECLARE-20260811-construction-contract-receipt.md` +2 |
| `:487` | `# zero. The flag makes "nobody checked" a readable state rather than an infe` | `:507` | `PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md` |
| `:489` | `ROOT.TParameter("int")("fixed_seed_null_checked", 1 if null_norm is not None` | `:509` | `receipt_candidate_stamps_5d.py` |
| `:491` | `ROOT.TParameter("double")("fixed_seed_null_norm", null_norm).Write()` | `:511` | `SCOREBOARD-20260817-quarantine-seven-causes.md` |
| `:498` | `print(f"[combine] wrote {args.out_root}")` | `:524` | `20260810T012645Z-repair7-transcript.txt` |
| `:509` | `"fixed_seed_null_checked": null_norm is not None,` | `:535` | `DETERMINATION-20260817-causes-3-4-provenance-measured.md` |
| `:525` | `ap.add_argument("--seed", type=int, default=1000)` | **LINE DELETED** | `VALIDATION_LEDGER.md`, `COST-20260817-mii-seed-scan-derivation.md`, `EXTENT-20260817-2850-a100h-scope-and-missing-legs.md` +2 |

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
