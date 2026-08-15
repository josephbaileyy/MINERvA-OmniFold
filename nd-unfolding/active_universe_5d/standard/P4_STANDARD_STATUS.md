# P4 standard-lateral — Agent-A-owned status receipt (2026-07-18)

**REPAIR-4 STARTED 2026-08-12 by Lane B, authorized by Session A (ownership handed over; A is
migrating).** Scope is code/tests/receipts only — **no cluster P4 run**, per Joseph's standing hold.
Increment 1 of the six ranked defects: **`p4_evidence.py` is de-rooted (OI-43)**. Its
`REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"` now reads `REPO = P.REPO_ROOT; ND = P.ND_ROOT`,
reusing the resolver repair-5 (D4a) already put in `p4_lib` — which this module was importing all
along. **The defect was disagreement, not just a literal:** every containment guard in `p4_lib`
checks against `p4_lib.REPO_ROOT`, while `p4_evidence` carried an independent root, so the two could
diverge and no guard could see it. Also removed an `os.makedirs` that ran at **import** time in a
module whose docstring says *"Read-only: opens nothing for write"* — creation now happens at the
write site, ordered before the first `.PENDING`. **This is the hold's named release condition.**
Power-tested both directions: 4 new tests, suite **111 → 115 green**, and the pre-fix form
reconstructed in a temp copy fails exactly the three de-rooting assertions
(`/pscratch` present, `P.REPO_ROOT` absent, import-time `makedirs` back). The negative control is a
committed test, not a note.

**Increment 2 — the three shell drivers, because increment 1 was necessary and NOT sufficient.**
`run_p4_standard.sh`, `run_p4_merge_audit_std.sh` and `run_p4_unfold_std.sh` all carried the same
`REPO="/pscratch/…"`, and two of them `cd "${ND}"` **before** invoking the now-de-rooted
`p4_evidence.py` — so the chain stayed pinned to one checkout *through the caller*. Fixing the callee
and not the caller is the class I had just cited in increment 1's own commit message (BEN-162/163),
which is why these tests cover all three drivers rather than the one file OI-43 names. Each now
derives `ND` from `${BASH_SOURCE[0]}` and `REPO` from its parent, and **fails closed with exit 3** if
no `p4_lib.py` sits beside it. `BASH_SOURCE` is safe for exactly these three — they carry no
`#SBATCH` header and run as `bash run_p4_*.sh` under an existing allocation; an sbatch-submitted
script is spooled by Slurm and would resolve to the spool copy. All three `bash -n` clean.

**These three tests EXECUTE the drivers** — the first behavioural tests in this suite. Suite
115 → **118**. Power-tested by reverting all three to the hardcoded form: each new test failed on its
own assertion, and the load-bearing one is **`expected exit 3, got 1`**. The un-de-rooted driver
*does* fail in a foreign tree — it fails late, for the wrong reason, with a generic abort code. **A
test asserting merely "nonzero" would have been green on the defect**, which is precisely what
defect 6 means by *"assert the specific intended failure, not a generic argparse nonzero"*. Restored
and re-verified by sha256 (`38721b9a…`, `dcae976a…`, `412086a3…`) plus a full green run.

Remaining: defects 1–6 of `followup-agent-A-standard-05.md`; ~~**stage 3
must still not run on pre-G-1 code** and **G-1 is not on the cluster checkout**~~ — **both stricken
2026-08-15 (`BEN-352`): G-1 IS on the cluster checkout and stage 3 ALREADY RAN on it, 2026-08-08. See the
correction block at the end of the 2026-08-07 addendum below.**

**VERIFIER STATE (2026-08-15, `repair-8`) — supersedes the repair-7 BLOCK cited anywhere below.**
`standard-p4-verifier` returns **`BLOCK`, `defects_outstanding: 10`,
`authorizes_covariance_stages_4_6: false`** at `code_rev 7d884da`. Receipt:
`../../../docs/orchestration/runs/standard-p4-verifier/20260815T232546Z-repair8-verdict.json`.
The repair-7 verdict was **measurably stale** — 25 of its 43 scope files changed, and 5 of its 14
defects are closed in tree. **The BLOCK now rests on defects #4 and #5, which are in the token gate
itself:** a symbolic `code_rev` such as `"HEAD"` passes the ancestry rule and then makes the gate's
own staleness check compare HEAD with HEAD, so it is vacuous. **Do not read the closures as movement
toward a PASS** — stages 4–6 are exactly as unauthorized as before. #6 is repaired at `0055826` and
**deliberately not certified**: its author called it Joseph's packet decision, and it awaits him, not
the lane. **This file's own line below — "NO covariance candidate exists" — is defect #9 and is FALSE
at HEAD** (5D and 4D candidates exist and were product-audited; see
`PROVENANCE-DEBT-20260810-standard-p4.md` §2b/§2c). It is left uncorrected here because the verifier
reviews and does not repair; correcting it is the lane's work.

**Current continuation (2026-08-11): Packet B channel PASS; real-cluster terminal verdict
pending.** PB1–PB5 implementations and adversarial acceptance evidence are committed at
`0055826`, `32489a6`, `c308a9c`, `ea89701`, and `64916ee`; PB5 is bounded/documented rather than
fixed. A 17-test current-tree focused check passes. Interactive allocation `56636802`, step
`56636802.0`, is the sole real-cluster writer: evidence is complete and stage 5/6 was still active
at reconciliation. The run is explicitly non-adoptable (`P4_NON_ADOPTABLE=1`, verifier token
unset). Watches cover the `STAGE56_END` log record and allocation terminal state. Packet B is not
cluster-closed until those artifacts are independently validated and the preserved
`standard-p4-verifier` UUID returns its scoped verdict. No adoption is authorized. Canonical
receipt: `../../../docs/orchestration/state/p4-packetb-channel-test-20260811T1211Z.json`.

Co-located Agent-A status (the canonical `ND_OMNIFOLD_STATUS.md` carries a concurrent
session's uncommitted edit and is NOT absorbed, per the commit-gate ownership rule — PG0).

**State: REPAIR round 3 complete; NO covariance candidate exists.** Candidate
construction (component-build → validate → project → adopt) is gated on the
standard-p4-verifier (019f74cb-…) returning PASS on the committed round-3 patch.

> **CORRECTED 2026-08-07 (BEN-046) — read this before sizing any remaining work.** The line
> above says "repair round 3 complete", which describes the work *submitted* and is silent on
> the *verdict returned*. The verdict was **BLOCK**: the same `standard-p4-verifier` UUID
> blocked `74fa362` with **six ranked defects**, and
> `docs/orchestration/followup-agent-A-standard-05.md` was written as the repair-4 brief.
> **No repair-4 commit was ever made** — `git log 74fa362..HEAD` over `p4_*` / `run_p4_*` /
> `tests/test_p4_repair.py` returns only `d5bd5da` (an unrelated note-overclaims commit that
> incidentally touched three of the same files), the FPS lane's own repairs, and the
> 2026-08-07 G-0/G-1/G-3 close-out commits. So the six defects are outstanding and stages 4–6
> are **not** merely awaiting a formality. `MIGRATION-TAKEOVER-STATUS.md` rows T2 and PG3S
> carry the BLOCK; `RUNBOOK-20260807-gbdt-closeout.md` §1 does not, which is the finding.

**Addendum 2026-08-07 — close-out packets G-0/G-1/G-3 (see the RUN_LOG entries of that date).**

- **G-1 landed (code only):** the lane can now express a background footing. `P4Config` carries
  a validated `bkg_mode` inside `config_hash`; `p4_evidence.py` writes a nested `footing` block
  plus per-endpoint `footing_evidence` classified from the unfold logs and blocks when they
  disagree; `run_p4_unfold_std.sh` passes `--bkg-mode` explicitly and stamps it into both
  receipt shapes. Value is `purity`, the recorded 2026-08-07 decision. Tests 41/41.
  ~~**Not yet on the cluster checkout** — that tree is shared with a live concurrent lane.~~
  **STRICKEN 2026-08-15 (`BEN-352`): G-1 IS ON THE CLUSTER CHECKOUT.** Measured this session — cluster
  `HEAD` = `683bdcc`, and `git merge-base --is-ancestor 5a4009f HEAD` in
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold` returns **true**. The wiring is live in that working tree —
  `run_p4_unfold_std.sh:37` reads `bkg_mode` from `P4Config`, `:90` passes `--bkg-mode`; **those are the
  CLUSTER tree's coordinates at `683bdcc`, and the same lines are `:41`/`:111` at local `HEAD`** (the
  trees are forked — `OI-74`). This line was true when written on 2026-08-07 and was never rechecked.
- **G-3 preflight PASSED** (job `56445593`, ~71 s): 10/10 merges valid, audit 120/120,
  `EVIDENCE-COMPLETE`, all five cross-checks MATCH, `mask5d n=10694`, `mask4d n=4830`.
- **Attestation is available, measured not assumed:** all ten endpoint ROOTs sha256-match the
  committed manifest (10/10), ~~so stage 3 legacy-attests with no re-unfold.~~ **STRICKEN: there is no
  legacy-attest path to take. It was DELETED, not repaired, in `2654731` (2026-08-08) —
  `run_p4_unfold_std.sh:85-103` retains the deletion rationale. Stage 3 can only PRODUCE, and the ten
  measured receipts say `mode=produced`, i.e. it re-unfolded.**
- ~~**Stage 3 deliberately NOT run:** on pre-G-1 code it would write ten receipts with no
  `bkg_mode`, and the launcher skips any endpoint that already has a receipt — with deletions
  frozen, that would be an unfixable provenance regression.~~
  **STRICKEN ON BOTH HALVES. (a) STAGE 3 RAN — 2026-08-08, post-G-1. (b) THE HAZARD WAS NEVER REAL after
  `febb9a1` (2026-08-07): the launcher skips only when `p4_check_receipt.py` PASSES, not on receipt
  existence (`run_p4_unfold_std.sh:77-84`). `bkg_mode` is a REQUIRED key (`p4_lib.py:796-797`, enforced
  `:949-950`) and is COMPARED (`:961-962`), so a receipt lacking it FAILS the gate, is `rm -f`'d, and is
  re-run transactionally. The gate cast as the trap is the repair mechanism; the cost is compute, not
  irreversibility.**
- ~~**Still true:** the ten ROOTs have **zero** `.done` receipts (`KNOWN_ISSUES.md` #20(c)).~~
  **STRICKEN — REFUTED BY MEASUREMENT: ten ROOTs and TEN `.done` receipts.**

> ### CORRECTION 2026-08-15 (`BEN-352`) — five counts above were stale; superseded text retained per this repo's convention (`c179a35`)
>
> **Measured this session, read-only, in
> `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/unfolds/`:**
> **ten ROOTs and ten `.done` receipts, all dated 2026-08-08**, each with
>
> ```
> mode      = produced
> bkg_mode  = purity
> code_rev  = 42268b6dfa2e60a0e4bd491b11ad9b11d0228273
> ```
>
> `42268b6` **contains** `5a4009f` (G-1), `febb9a1` (the resume-gate repair) and `2654731` (the
> legacy-attest deletion) — each verified by `git merge-base --is-ancestor`. Receipt `t` stamps run
> `2026-08-08T13:41:45Z` → `14:59:03Z`; ROOT mtimes `06:40`–`07:59` local. **STAGE 3 RAN, POST-G-1, ON
> 2026-08-08.**
>
> The run sits inside holder allocation **`56495756`** (`gbdt-hold`, `WorkDir`
> `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, start `2026-08-08T05:21:41`, allocation `TIMEOUT` at
> `08:21:46`); step **`56495756.0`** (`bash`) ran `05:21:46`→`07:59:04`, `COMPLETED`, elapsed `02:37:18`.
> The last receipt is stamped `07:59`, four seconds before that step ended — so **stage 3 completed inside
> the step and the allocation's `TIMEOUT` is the holder expiring afterwards, not a failed unfold.**
>
> **TWO THINGS THIS CORRECTION DOES NOT RESOLVE. Both are escalated, not adjudicated — `OI-75`.**
>
> 1. **THE RUN IS UNRECONCILED WITH THE HOLD AT LINE 4 OF THIS FILE.** That line records Joseph's
>    standing hold — scope *"code/tests/receipts only — **no cluster P4 run**"* — and **there is no record
>    of the 2026-08-08 run anywhere in this repo**: no RUN_LOG entry, no ledger row, no products summary.
>    **Whether it was authorized is Joseph's question. It is already put to him and unanswered.** This
>    file records the discrepancy and takes no position. **The artifacts being well-formed is not evidence
>    that the run was authorized** — a correct receipt attests to provenance, never to permission.
> 2. **THE TEN PRODUCTS ARE UNTRACKED AND EXIST ONLY ON PURGEABLE SCRATCH.** `git ls-files` over that
>    directory returns **0** on both the cluster and local checkouts, and `git status --ignored` reports
>    every ROOT as `!!`. By this repo's own rule — *a result does not exist until its commit lands* —
>    **they do not exist, and that is exactly why five documents say stage 3 never ran.** The products
>    total **4.8 MB** (ten ROOTs at ~480 KB each), *not* the 20 GB an earlier relay of this escalation
>    assumed; the 53.8 GB × 10 figure in `p4_lib.py:790` is the **merged inputs**, not these outputs. The
>    size is recorded to keep the disposition honest and **is not a recommendation to commit them** —
>    that is a provenance and authorization decision, not a storage one, and it is blocked on item 1.

- **P3S:** 120/120 endpoint event loops done.
- **Merge:** 10/10 endpoint MEFHC ROOTs. Full-file hashes validated by the owner-neutral
  orchestrator receipt `docs/orchestration/state/merged-input-hashes/p4-merged-20260718/`
  (COMPLETE; size⇥mtime⇥path inventory; 10-line standard.sha256) — reused, NOT re-hashed.
- **Unfold:** 10/10 endpoint xsec ROOTs content-validated (open/non-zombie/not-recovered/
  finite `hXSecND_flat`/65856-bin/positive/10694-central-mask/distinct). ~~Legacy products
  (no `.done`) are attested read-only against the manifest;~~ **stricken 2026-08-15 (`BEN-352`) — that
  path was deleted in `2654731` and the live products are `mode=produced` with `.done` receipts;** the
  transactional driver (`run_p4_unfold_std.sh`) writes the receipt LAST after an atomic ROOT publish.
- **Evidence:** EVIDENCE-COMPLETE. Recomputed bindings MATCH the verifier's independent
  observations — central5d `630306e2…`, mask5d `74374b1a…` (10694), endpoint-manifest
  `af568b4a…`, central4d `1fb82508…`, mask4d `c977c643…` (4830). New round-3 bindings:
  config-hash, source git blobs+commits, C++ binary sha256 `6b60fc51…`, edges/bin-volume
  hash (`e05889ac…`/`f71145ce…`), endpoint mask-equality TRUE, orchestrator merged digest
  `6e6c4752…` (10 hashes). Selection migration: BeamAngleX/Y nonzero (4700–4808),
  MuonResolution/Muon_Energy 0 (bin-migration-only) — as expected. Receipts under `evidence/`.
- **Hardening (round 3):** ROOT lazy-imported everywhere (guards/tests run login-side);
  separate canonical stat/ML ROOTs + PURE ADDITION (no subtraction) in
  `p4_build_components.py`; deterministic in-code projection M + byte-identical central
  non-mutation (`p4_project_4d.py`); inseparable merged-evidence gate; later-only adoption
  CLI `p4_adopt_standard.py` (not run/not wired); real-CLI harness `tests/test_p4_repair.py`
  — 28/28 PASS. Canonical driver `run_p4_standard.sh` STOPs at evidence by default and
  requires a `P4_VERIFIER_PASS` token before any covariance stage.

Downstream (P5B/P6) consume ONLY after PASS + a later, separately authorized candidate turn.
