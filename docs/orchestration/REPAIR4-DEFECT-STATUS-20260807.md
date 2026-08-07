# Repair-4 scope — the six verifier defects and their status at HEAD (2026-08-07)

> ## OUTCOME 2026-08-07T13:46Z — repair-4 returned **BLOCK**, 2 of 6 closed
>
> An independent read-only `codex-school` pass over repair-4 at `39c2cf4` **closed defects 1
> and 5** and left **four outstanding**. Receipt + full transcript:
> `runs/standard-p4-verifier/20260807T134623Z-repair4-verdict.json`. `P4_VERIFIER_PASS` was
> **not** set; stages 4–6 remain unauthorized. The delegate wrote nothing (`git status` clean
> afterwards, no diff to preserve).
>
> **Tests: the delegate reported 82/99; a local re-run at the same commit is 99/99.** The 17
> shortfalls are an environment artifact — the read-only sandbox has no writable temp dir, so
> every `tempfile.TemporaryDirectory()` test errored before reaching an assertion. The delegate
> diagnosed that itself and did not count it against the code. **Do not "fix" 17 phantom
> failures.**
>
> **The four outstanding items, all accepted as correct:**
>
> 1. **D2 — the receipt gate checks `code_rev` for non-emptiness and nothing else.** No source
>    blob or commit identity is recorded or compared, so an endpoint produced under changed
>    source still skips. This is the *same* anti-pattern this lane already recorded as
>    `KNOWN_ISSUES.md` #21 — written into the very gate meant to end it.
>    `p4_lib.py:278,302`, `run_p4_unfold_std.sh:81`.
> 2. **D3 — the dirty-source guard is fail-OPEN on deletion.** `need(_w is None or _c == _w)`
>    passes when `git hash-object` fails on a missing file, so deleting a bound source is
>    accepted. `p4_evidence.py:246`.
> 3. **D4 — containment is still escapable, and the identity claim overreaches.** The
>    component-sequence match succeeds anywhere the sequence appears, so
>    `/evil/active_universe_5d/standard/candidate/out.root` passes, and `normpath` does not
>    resolve symlinks; it must be realpath-based against the repo root. Separately, PSD of
>    `C_combined − C_syst` is *necessary but not sufficient* for
>    `C_combined = C_syst + C_stat + C_ML` — it never compares the residual to the bound
>    stat+ML blocks. `p4_lib.py:190,200`, `p4_validate_active_lateral.py:128`.
> 4. **D6 — coverage still does not execute a shell driver or a builder→validator happy path,**
>    and `test_validator_recomputes_the_full_total_identity` blesses the weaker PSD check under
>    a stronger name. The shell-driver gap was *disclosed* in the test docstring, but disclosure
>    is not coverage; and a test that names a weaker check as a stronger one is the defect-6b
>    family this round was supposed to end.
>    `tests/test_p4_resume_integration.py:159`, `tests/test_p4_repair.py:683`.
>
> **Repair-5 is scoped to exactly those four.** Defects 1 and 5 are closed and should not be
> re-opened. `4d` (no promotion in `p4_adopt_standard.py`) was judged an acceptable
> non-repair — adoption is out of scope and the chain stops at CANDIDATE.

**Purpose.** Scope repair-4 from *all six* defects the `standard-p4-verifier` raised, not from the one
that was independently re-confirmed. Authorized by Joseph 2026-08-07 after he verified defect 1 himself.

**Source of the six.** The verifier's own final message, committed in this repo at
`docs/orchestration/runs/standard-p4-verifier/20260718T182040Z-send-8e4ca3d7.jsonl` (last
`agent_message`, 12,143 chars, opens `BLOCK`). Not a paraphrase from `followup-agent-A-standard-05.md`,
which is the derived brief. Every status below was re-checked against HEAD (`59f728e`) in one session
and cites the line it was read from.

**Verdict scope reminder.** The verifier also recorded *verified foundations* that still hold and must
not be re-litigated: the owner-neutral merged receipt (10/10 hashes, all live sizes/mtimes match), all
ten endpoint SHA256s equal to the manifest, endpoints finite/positive/65856-bin/10694-mask with
genuinely asymmetric pairs, migration 4700–4808 on `BeamAngleX/Y` and zero elsewhere, and MAT centering
as the required biased `1/N`. Re-verified independently 2026-08-07: 10/10 endpoint sha256 match, and
`EVIDENCE-COMPLETE` with all five cross-checks MATCH.

---

## Status summary

| # | Defect | Status at HEAD |
|---|---|---|
| 1 | Driver disconnected from the real CLIs | **LIVE — all 4 sub-parts** |
| 2 | Resume/completion not config- or source-validating | **LIVE (4 of 5)** — merge helper sub-part REPAIRED |
| 3 | Manifest internally inconsistent, absorbed a dirty source | **LIVE — all 4 sub-parts** |
| 4 | Component/adoption provenance separable | **PARTIAL** — candidate-hash binding repaired; 4 sub-parts live |
| 5 | Projection does not bind all mandatory geometry | **LIVE — all 4 sub-parts** |
| 6 | Tests lack integration coverage | **LIVE**, incl. a still-green false-positive test |

Nothing in the 2026-08-07 G-0/G-1 packet repaired any of the six; G-1 added a footing field, an
orthogonal concern. Two sub-parts were repaired incidentally by `d5bd5da` (2026-08-02), a
note-overclaims commit — see 2e and 4c.

---

## 1 — The authoritative driver is disconnected. **LIVE (4/4)**

Stages 4–6 cannot execute; this is `KNOWN_ISSUES.md` #22, and Joseph re-confirmed 1b–1d independently.

- **1a — stage order.** Driver still runs evidence *before* unfold (`run_p4_standard.sh:35` evidence,
  `:37` unfold), against the required merge → audit → unfold → endpoint-evidence sequence. **LIVE.**
- **1b — validator CLI.** Driver passes `--active … --support … --merged-dir …`
  (`run_p4_standard.sh:49-52`); validator requires `--candidate --support --manifest --merged-audit
  --out`, all `required=True` (`p4_validate_active_lateral.py:35-39`). Two passed options do not
  exist; three required ones are absent. **LIVE.**
- **1c — projector CLI.** Driver passes `--proj` (`run_p4_standard.sh:54`); projector defines only
  `--c5 --manifest --out --central-rel` (`p4_project_4d.py:46-49`). **LIVE.**
- **1d — nonexistent ROOT key.** Driver names `hCov_std_final5_candidate` (`:50`, `:53`); repo-wide
  grep finds it **only** on those two lines. Builder writes `hCov_active5d_<band>`,
  `hCov_active5d_total`, `hCov_stdsyst5d_total_candidate`, `hCov_stdcombined5d_total_candidate`
  (`p4_build_components.py:159-162`). **LIVE.** Also `AGENT_A_HANDOFF.md:95` still repeats the stale
  order and `--merged-dir` contract.

**Treat as unexercised code, not typos.** `STOP_AFTER` defaults to `evidence`, so stages 4–6 have
never run. Renaming flags would give a chain that executes and is still wrong — the order fix (1a) and
the handoff are part of the same defect.

## 2 — Resume/completion is not config- or source-validating. **LIVE (4/5)**

- **2a — skip is content-blind.** `run_p4_unfold_std.sh:45` skips on
  `[[ -s OUT && -s REC ]] && valid_root OUT`. Receipt tag, ROOT SHA, merged SHA, central SHA, config
  hash and source hashes are never read. **LIVE.**
- **2b — legacy receipts omit provenance.** The legacy-attest receipt carries no `merged_sha256`,
  `central5d_sha256`, or source hashes. G-1 added `bkg_mode` only. **LIVE.**
- **2c — receipt-write failure not propagated.** After the atomic ROOT rename the
  `printf … && mv` result is unchecked, so a worker can print `DONE` and return 0 with no valid
  receipt. **LIVE.**
- **2d — extra endpoint tags not rejected.** Inventory asserts the ten expected tags exist; it never
  rejects an eleventh. **LIVE.**
- **2e — merge helper fail-closed.** **REPAIRED** by `d5bd5da`: PIDs collected and waited
  individually, `NFAILED` aggregated, `EXPECTED=10` asserted (`run_p4_merge_audit_std.sh:26-48`, with
  the J31 rationale in-comment).

**Interaction with G-3.** 2a/2b are why stage 3 has not been run: attesting today writes ten receipts
in the incomplete legacy format, and 2a then skips them forever. Repair 2 **before** attesting.

## 3 — Manifest internally inconsistent, absorbed a dirty source. **LIVE (4/4)**

- **3a — config not fully hash-bound.** `p4_evidence.py:160` computes `config_hash`, then `:161` adds
  `full_phase_space_reported_grid` to `man["config"]`. The recorded hash does not cover the recorded
  config. **LIVE.**
- **3b — blobs hashed from the working tree, not commit objects.** `p4_evidence.py:137-141` hash
  working paths; `:150-151` hash the C++ binary as it is on disk. This is how the unrelated dirty
  OmniFold blob was absorbed in 2026-07. Re-demonstrated 2026-08-07: regenerating moved
  `binary_sha256` and two `source_blobs` while every physics binding stayed byte-identical
  (`KNOWN_ISSUES.md` #23). **LIVE.**
- **3c — source commits misattributed.** Consequence of 3b: recorded commits need not be the commit
  that introduced the recorded blob. **LIVE.**
- **3d — endpoint identity and migration under-checked.** `p4_evidence.py:153` asserts `band_meta`
  only; `idx_meta` is recorded at `:141` and **never asserted**, so `(band,index)` identity is not
  proven. `:156` enforces nonzero migration for `NONZERO_MIG`, and **`ZERO_SEL` (`:37`) is never
  referenced by any check** — a dead constant, so zero-migration is never enforced. **LIVE.**
- **3e — validator ignores the audit content.** It now *takes* `--merged-audit` and loads it
  (`p4_validate_active_lateral.py:38,51`) — a `d5bd5da` improvement — but a grep for
  `selection_migration_abs|census|tree_entries` in that file returns **0**. It reads the file and
  checks none of it. **LIVE.**

## 4 — Component and adoption provenance separable. **PARTIAL**

- **4a — not every retained pure component is persisted.** Builder writes five active bands plus three
  totals (`p4_build_components.py:159-162`); retained non-active blocks are not written. **LIVE.**
- **4b — manifest written before the candidate.** `json.dump(prov, …)` at `:150` precedes
  `ROOT.TFile.Open(a.out, "RECREATE")` at `:153`, so a manifest can exist for a candidate that was
  never completed — the inverse of the receipt-last discipline used elsewhere. **LIVE.**
- **4c — adoption no longer accepts any readable candidate.** **REPAIRED** by `d5bd5da`: requires
  `--i-understand-adoption` (`:24`), validator `result == "PASS"` (`:27`), per-input identity
  (`:32-33`), `pure_addition` (`:34`), out-aliasing refusal (`:38`), and binds
  `val["candidate_sha256"] == sha256_file(candidate)` (`:44-50`, the J32 fix).
- **4d — adoption still performs no promotion.** It prints `"gates PASS; would promote …"` and
  `sys.exit(0)` (`p4_adopt_standard.py:51-53`). No atomic allowlisted promotion exists. **LIVE**
  (harmless while adoption is out of scope, but it is not a working adoption path).
- **4e — candidate-path guard is substring-based.** `p4_lib.py:175` uses `CANDIDATE_SUBDIR in path`,
  not resolved containment, so a traversal through a path *containing* the candidate directory passes.
  **LIVE.**
- **4f — validator does not consume the component manifest** or independently prove the full-total
  identity. **LIVE.**

## 5 — Projection does not bind all mandatory geometry. **LIVE (4/4)**

- **5a — edge-hash check is optional.** `p4_project_4d.py:62` guards on `if "edge_hash" in man`, so a
  manifest without the key silently skips it. **LIVE.**
- **5b — bin-volume hash never validated.** Computed and written into the receipt (`:84`) but never
  compared to the manifest. **LIVE.**
- **5c — 4D mask hash not checked.** `:67` compares only the reported *count*
  (`int(m4.sum()) == man["mask4d_nreported"]`), not `mask4d_hash`. **LIVE.**
- **5d — no `M`-content hash.** Only `M_shape` is recorded (`:88`). **LIVE.**

Note the caveat already recorded in `RUNBOOK-20260807-gbdt-closeout.md` §7.4: `mask_order_hash` has no
pinned canonical target on the standard side, unlike FPS's `REPORTED_MASK_FINGERPRINT`. So 5c can prove
all components share *one* mask, not that it is the declared publication mask. **If the note quotes a
reported-bin count, pin the target constant first.**

## 6 — Tests lack integration coverage. **LIVE**

- **6a — nothing executes the shell drivers.** No test runs `run_p4_standard.sh` or
  `run_p4_unfold_std.sh`. G-1's `test_launcher_passes_bkg_mode_explicitly` asserts on the launcher's
  *text*, which is a contract check, not execution. **LIVE.**
- **6b — a green test that proves nothing.** `test_project_rejects_protected_out_path`
  (`tests/test_p4_repair.py:214-222`) still passes `--proj`, which no longer exists, so argparse exits
  nonzero **before the path guard runs**. The assertion `assertNotEqual(rc, 0)` passes for the wrong
  reason. This is the verifier's named false positive and it is still green today. **LIVE.** The fix
  is to assert the *specific* gate or error reached, never merely a nonzero return.
- **6c — missing matrix.** No fake producer, worker-failure aggregation, receipt resume/staleness,
  ordering, builder→validator happy path, or adoption identity test
  (`followup-agent-A-standard-04.md:57-62`). **LIVE.**

---

## Sequencing note for repair-4

2 must land before G-3's attest step, or attestation bakes in incomplete legacy receipts that 2a then
skips permanently (deletions are behind the reorg freeze tag). 1 and 6b are the cheapest and the most
misleading if left. 3b is shared with `KNOWN_ISSUES.md` #23. 4d is out of scope in effect — **the
adoption boundary stands; repair-4 and a green chain reach a CANDIDATE and no further.**

Tests must be built by calling the real producers, or by copying their literal output — never
hand-assembled to match the consumer (BEN-040, and 6b is what the alternative looks like).
