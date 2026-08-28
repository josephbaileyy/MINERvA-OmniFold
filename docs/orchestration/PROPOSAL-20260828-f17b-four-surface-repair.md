# PROPOSAL — bounded four-surface repair of the F-17(b) comparison instrument chain

> **STATUS: PROPOSAL ONLY. THIS DOCUMENT AUTHORIZES NOTHING.** It is submitted for a separate
> decision by the delegated authority. It implements no repair, launches no compute, requests no
> rehearsal, grades nothing, adopts nothing, and moves no gate. Gate 2 remains **FAIL**; readiness
> remains **NOT READY**; no scalar-5D covariance is adopted.

- Authored: 2026-08-28 by the accountable root (`claude-school`, thread `66a7e51b-abea-42d6-b8c1-b61952d5ec2b`).
- Occasioned by: `evt-user-authorized-root-probe-20260828t1019z`; see
  `docs/orchestration/state/RECEIPT-20260828-user-authorized-root-probe.json`.
- Measured at: `HEAD 7a52652` (canonical `main`, clean worktree). **LIVE-STATE was STALE when this was
  written** (`Git: fe209bce`, `HEAD 7a52652`, `HEAD^ 6828074`); every fact below was therefore
  re-measured directly rather than quoted from the generated view.

## 1. Scope — exactly four surfaces, and nothing else

| # | Surface | SPEC | Files that must change |
|---|---|---|---|
| 1 | Emit a real measurement wall-clock | **R6** | `measure_m1_m6.py` **and** `compare_m1_m6.py` |
| 2 | Emit detached-or-branch identity | **R3** | `measure_m1_m6.py` **and** `compare_m1_m6.py` |
| 3 | Digest-bracket the **preserver** across its own invocation | — | `measure_k0_farend_f1b_f17b.sh` |
| 4 | Short-circuit immediately on a nonzero measurer rc | — | `measure_k0_farend_f1b_f17b.sh` |

Nothing outside this table is proposed. In particular this proposal does **not** touch the
`:1471` half of F-17(b), which is impossible for this rehearsal by construction.

## 2. Measured basis (re-measured at `HEAD 7a52652`, not quoted)

| File | sha256 | bytes | lines | MANIFEST row |
|---|---|---|---|---|
| `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `c40e6b54…` | 15722 | 236 | line 198 |
| `docs/orchestration/measure_m1_m6.py` | `0fcd90f7…` | 13213 | 272 | line 199 |
| `docs/orchestration/compare_m1_m6.py` | `5dc92487…` | 66599 | 1084 | line 182 |

Surface-by-surface confirmation that the chain is unrepaired:

- **R6 / R3 are hardcoded on the comparator side.** `compare_m1_m6.py` `identity_of()` sets
  `"measurement_wall_clock": UNAVAILABLE` at **:440** and `"branch_or_detached": UNAVAILABLE` at
  **:446**. Its own docstring names these "the two fields the input schema cannot supply".
- **The measurer supplies neither.** `grep -c 'wall_clock\|branch_or_detached' measure_m1_m6.py` = **0**.
- **Therefore surfaces 1 and 2 require BOTH instruments.** Repairing `measure_m1_m6.py` alone cannot
  discharge R3 or R6, because the comparator would keep overwriting the fields with `UNAVAILABLE`.
  `compare_m1_m6.py:925-926` independently records the same diagnosis in prose.
- **Surface 4 is real but hardening only.** `measure_k0_farend_f1b_f17b.sh:172-174` captures `rc=$?`,
  prints it and tails the `.err`, then continues. The chain nonetheless stays **fail-closed**: the
  comparator gate at **:207-212** is `case "$crc" in 0|10|20) ;;` with an explicit refuse-and-exit
  otherwise, so a comparator refusal (exit 4) falls outside the gate and publishes no durable record.
  Surface 4 therefore buys **wasted-work avoidance, not integrity**, and must not be sold as the latter.

## 3. Coupling and pin obligations — WIDER than the generated view states

The stale LIVE-STATE flagged MANIFEST/F-14 coupling for the shell script only. Measured: **all three
files are MANIFEST.tsv rows**, and their rows carry line and byte counts that this repair changes.
Any decision to proceed must budget for all three row updates, not one.

Two existing pins of `measure_k0_farend_f1b_f17b.sh` are invalidated by surface 3 or 4:

1. **Decision section 11** (`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md:561,614`) pins it
   at content sha256 `c40e6b54`, 15722 bytes. **Verified live: still exact.** This pin is currently
   TRUE and the repair makes it FALSE.
2. **`docs/orchestration/receipts/RECEIPT-20260825-terminal-watch-f17b-durability.json:10`** pins it at
   `2132194fe1a3ed7a420f19b7b8b7d2f23fed873c12c316fc525a85b11a1253a2`. **Verified live: this does NOT
   match the current file**, so this pin is **already superseded in fact** and is a pre-existing
   defect independent of this proposal.

Each must be **SUPERSEDED by a new dated row stating old value, new value, and reason** — never
silently repointed. Neither pin may be edited in place to make a check pass.

> **Routing correction, so the successor does not inherit a mis-citation.** The stale LIVE-STATE
> attributes the supersession rule to `OI-123`. I read `OI-123`: it does not contain that sentence.
> `OI-123` is the `step1_increment_trajectory.py` pin landmine (`48f8353d` → `ca2128ac`) affecting
> three Gate-6 Leg F / Leg X launchers; its operative content is a two-way choice — (a) freeze
> `gate6-reconcile-56834281` and give every future leg its own checkout, or (b) re-issue the
> floor-replicate and legx launchers *with their owning receipts* — plus one prohibition:
> **do not re-pin a receipt-bound launcher to make the check pass** (`verify_hash_bindings.py`
> refuses; `BEN-270`). `OI-123` also records the landmine is fail-closed and loud (`die … 3` before
> any GPU work, zero GPU-hours), i.e. "fix before submitting", not "fix now".
> The supersession discipline is real and applies here via **F-14 / section 7.0.7** and the MANIFEST
> rows. Cite it there. `OI-123`'s prohibition is what forbids the in-place edit of pin 2 above.

The nine MANIFEST referrers of the shell script include `GRADE-20260825-f17b-comparison-instrument-fitness.md`,
`MEASUREMENT-20260822-m1-m6-at-pinned-sha.md`, `RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md`,
`REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, `preserve_f17b_record.py`, and
`state/f17b-k0-aa67c426-20260824T145751Z.json`. Their routes should be checked for stale hash text
before the repair is declared complete.

## 4. What a decision to proceed would and would not buy

**Would:** permit implementing exactly surfaces 1–4, followed by a **fresh independent full-chain
grade** by a reviewer who is neither the implementer nor `agy-capacity-probe` (already used, and
therefore disqualified for the post-repair grade).

**Would NOT, even on a FIT verdict:** turn this rehearsal's Gate 2 into PASS. Three of the six
independently sufficient clauses at `327bc105` — F-2(b), F-3(b), F-5(b) — need **producer filings that
do not exist**, and F-17(b)'s `:1471` half is impossible for this rehearsal by construction. A FIT
would authorize only *proposing a NEW forward-only rehearsal*. Nothing in this proposal shortens the
scalar-5D path: no covariance candidate is adopted, and every non-2D publication covariance must still
project from the eventual adopted trunk.

## 5. Explicitly out of scope (settled; do not re-commission)

- Another section 10.1 readiness check — F-7(b) and F-8(b) readiness **are** satisfied at this tip.
- Another F-17(b) mechanism grade of the **unrepaired** chain — recorded NOT FIT.
- Any re-grade of the dirty-warning delivery — graded and landed.
- Reopening `OI-126` — RULED; PET is diagnostic/method development, off the publication path.
- Any `C_ML` construction or Gate-6 compute change; any repeat of completed 2D/3D/4D/5D central-value
  or closure campaigns.

## 6. The decision requested

**One decision:** proceed, or do not proceed, with the bounded four-surface repair as scoped in §1,
subject to the pin-supersession and MANIFEST obligations in §3 and the reviewer-independence
requirement in §4. Reserved to Joseph or the delegated authority. The root will not implement absent
that decision.
