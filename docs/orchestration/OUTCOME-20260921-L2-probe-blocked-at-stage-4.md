# OUTCOME 2026-09-21 — the `L2` probe produced ten member unfolds and **no `s_proj`**: stage 4 is gated

**CITABLE FOR:** what the probe produced, what it proved about its own machinery, and the
authorization gate that stopped it.
**NOT CITABLE FOR:** any value of `s_proj` with the five lateral bands released — **there is none** —
any statement about `L2`'s direction, any regrade, or any change to the adoption.

This record discharges the third row of
[`PREDECLARATION-20260921-L2-lateral-seed-release.md`](PREDECLARATION-20260921-L2-lateral-seed-release.md)
§4's fixed outcome map:

> | **cannot be computed** | the probe failed; report the inability as an inability | it is not a result of any kind |

**That row was written before the run, and it is the row that applies.** Nothing below reinterprets
it.

---

## 1. ⚠ THE ANSWER TO THE QUESTION THE PROBE ASKED IS: STILL UNKNOWN

`L2` asked whether the `L1` FAIL survives releasing the five seed-pinned lateral bands. **It is not
answered.** `s_proj` with the five released was never computed, so:

- `L2`'s direction remains **UNKNOWN**, exactly as
  [`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md)
  left it. The withdrawal of the *"lower bound"* reading stands and is not weakened.
- `L1`'s `s_proj = 6.145%` against the `5%` bound is **untouched** — it was measured directly, never
  rested on this probe, and no number in it moved.
- The adopted digest `3d7465f6…`, cause 3's grade, and the absence of a quoted significance are all
  **unchanged**.

## 2. What the probe DID produce, and it is not nothing

| product | state |
|---|---|
| ten endpoint unfolds at estimator seed **1242** (`42 + 1200`), member-scoped | **published**, ROOT + receipt pairs, `mii/member_k001200/` |
| the member's `p4_standard_manifest.json` | **EVIDENCE-COMPLETE**, `rc=0`, consumable names |
| the member candidate (five active bands) | **NOT BUILT** — §3 |
| the member covariance | **NOT ASSEMBLED** |
| `s_proj` with the five released | **NOT MEASURED** |

**Uniform seed, proven across ten independently written receipts:** exactly **one** distinct
`config_hash` — `4809b4ad399f999c…` — over all ten, against the baseline's
`4b41fab90a83df08…`. That discharges §6's first invalidating condition ("the ten new unfolds not all
at the **same** seed `1242`") by measurement rather than by intent.

**The seed reached the estimator**, which is the premise the probe would have been worthless without:
the ten member endpoints diverge from the offset-0 reference by **12–15% per bin** and `~1e-3` on the
integral — eight orders above the `1.9e-11` reproducibility floor. `p4_evidence`'s inverted gate
reports **10/10 diverged, 0 reproduced**.

⚠ **None of that is a result about the covariance.** The band enters `C_Z` through the MAT `±`
*difference*, and the offset moves both endpoints of a pair together by construction. A 12% shift per
endpoint implies nothing about the band, and nothing about `s_proj`.

## 3. ⚠ WHY IT STOPPED: an authorization gate, functioning correctly, that I may not satisfy

`p4_build_components.py` is self-gated (repair-12) and refuses without `P4_VERIFIER_PASS` — the
sha256 of a **committed** `standard-p4-verifier` verdict carrying
`authorizes_covariance_stages_4_6=true`.

> FAIL-CLOSED :: stage 4 (components): covariance construction requires `P4_VERIFIER_PASS` … This
> module is gated on its own, not only through `run_p4_standard.sh`, so invoking it directly does not
> skip the gate (repair-12).

**Both committed verdicts were tested with the real checker, not read:**

| verdict | verdict field | result |
|---|---|---|
| `20260815T232546Z-repair8-verdict.json` | `BLOCK` | `TOKEN-REJECT` — "authorizes nothing" |
| `20260816T220615Z-repair11-verdict.json` | **`PASS`**, `authorizes_4_6: true` | `TOKEN-REJECT` — **13 files in scope changed at HEAD** |

> *"A PASS cannot authorize code the verifier never saw; re-run the verifier."*

### ⚠ 3.1 THE GATE WAS ALREADY UNSATISFIABLE BEFORE `L2`, AND THAT IS MEASURED

The same token against **`f6f54e73`** — the commit immediately before any `L2` code — **also
rejects, with 10 changed files.** So stage 4 was blocked for the entire standard-P4 lane before this
work began. `L2` took the changed-scope set from **10 → 13**:

| added by `L2` | already changed, not `L2`'s doing |
|---|---|
| `p4_check_receipt.py` | `p4_lib.py`, `p4_evidence.py`, `p4_build_components.py`, `seed_offset_policy.py` |
| `run_p4_standard.sh` | `p4_check_verifier_token.py`, `p4_project_4d.py`, `p4_validate_active_lateral.py` |
| `run_p4_unfold_std.sh` | `project_cov_nd.py`, `unfold_nd_omnifold_unbinned.py`, `uq_math.py` |

**This is stated to bound blame in both directions.** `L2` did not create the blocker and `L2` cannot
be blamed for the lane's inability to build a covariance; equally, `L2` did add three files to the
set a verifier must now cover, and pretending otherwise would understate what a re-run has to review.

### 3.2 ⚠ WHY THIS LANE DOES NOT ISSUE ITSELF A TOKEN

The remedy the gate names is *"re-run the verifier"* — an independent review role. **This lane
authored all eight sites under review.** `p4_check_verifier_token.py`'s own docstring records why the
gate exists at all:

> It was demonstrated load-bearing on 2026-08-07: an autonomous run that **self-authorized** would
> have written a candidate ROOT at stage 4 and died at stage 5 …
> **The fix is deliberately not "check the variable harder."** An agent that can set an env var can
> also write a JSON file, so a token bound to a file the agent could create is no gate at all.

Writing a verdict for my own change is exactly the act that sentence forbids, and a **compute** grant
is not a **review** authorization. Joseph authorized the estimator change and the probe; he did not
authorize this lane to certify its own code, and the two are not interchangeable. **The gate is not
routed around, not weakened, and not re-read for a softer clause.**

## 4. What would unblock it — routed, not performed

1. **A `standard-p4-verifier` re-run** over the current execution surface, by a lane that did not
   author the change, issuing a verdict with `verdict: "PASS"`,
   `authorizes_covariance_stages_4_6: true`, a **literal 40-hex** `code_rev` that is an ancestor of
   `HEAD`, and its scope byte-identical between that commit, `HEAD` and the working tree.
   ⚠ **This unblocks stages 4–6 for the whole standard-P4 lane, not only `L2`** — see §3.1.
2. Then stages 4 → 5 → 6, all scripted and ready: member candidate, one-row manifest swap, and the
   measurement — which re-derives the graded pair's `s_proj` as a control and **declares the
   released-lateral number uninterpretable** unless the control reproduces
   `6.145388143592225%` to `1e-12`.

**Cost of the remaining compute, measured rather than estimated:** the ten unfolds cost ~23 min each
at `CONC=2`; stages 4–6 are minutes. The expensive part is already spent and is **preserved** — the
ten member endpoints are published and resume-skip, so a verifier PASS makes the rest cheap.

## 5. What this probe proved about the eight-site change, on real artifacts

Recorded because it is the durable part, and because the change landed regardless of the probe:

- **The adopted covariance's inputs were never touched.** All **20** files (10 ROOT + 10 receipt)
  byte-identical before and after, re-hashed independently of the job that could have violated them,
  with the population asserted `20/20` first so the comparison could not pass vacuously.
- **The baseline manifest was never deleted.** `71aace382e8b0450…` before and after the member
  evidence run — the run which, unmodified, would have removed it and left a `.FAILED` in its place.
- **The provenance lie is closed.** Member receipts stamp `config_hash 4809b4ad…`. Before the repair
  they would have stamped `4b41fab9…` (seed 42) for a ROOT produced at 1242, and
  `p4_check_receipt` would have re-derived the same wrong value and **passed**.
- **Offset-0 is neutral by measurement**, on the cluster: the baseline config hash equals the adopted
  receipt's `4b41fab90a83df08…` exactly.
- **A live, pre-existing hazard is now fail-closed:** all ten adopted receipts are stale
  (`10/10 RECEIPT-REJECT`), so `bash run_p4_unfold_std.sh` re-unfolded over the published result's
  inputs, exit 0, silently. Guarded at `e2632ac7`.

**Co-Authored-By: Claude Opus 5 (1M context)**

---

## 6. ⚠ WHERE THE SPENT COMPUTE LIVES — **do not prune this worktree**

§4 says *"the expensive part is already spent and is PRESERVED"* and then does not say **where**,
which makes the sentence useless to the person who acts on it. Fixed here.

| | |
|---|---|
| worktree | `/pscratch/sd/j/josephrb/MINERvA-OmniFold-l2-20260921` — a **detached** worktree of the deployed repo at `c05c64a9`, registered in `git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold worktree list` |
| ten member unfolds | `<worktree>/nd-unfolding/mii/member_k001200/active_universe_5d/standard/unfolds/` — 10 ROOT + 10 receipt pairs |
| member manifest | `…/standard/evidence/p4_standard_manifest.json`, sha256 `aa5c22226f2ac84b…` |
| cost to recreate | ~10 × 23 min of CPU, through a saturated queue (11 idle nodes of 2853 when this ran) |

**The ten, pinned so a later lane can prove it is reading the same products:**

| tag | `sha256` (first 16) |
|---|---|
| `BeamAngleX_0` | `e6a8bbd1c74be79d` |
| `BeamAngleX_1` | `841777ee82f83437` |
| `BeamAngleY_0` | `8da8b3b95116d1ec` |
| `BeamAngleY_1` | `1c90395d11cb28ff` |
| `Muon_Energy_MINERvA_0` | `486c044d8a099046` |
| `Muon_Energy_MINERvA_1` | `bb9cec0f0505c9d8` |
| `Muon_Energy_MINOS_0` | `676a9a9996d31d9c` |
| `Muon_Energy_MINOS_1` | `ac8d1bf9dfa68559` |
| `MuonResolution_0` | `61eaa01773b5b172` |
| `MuonResolution_1` | `3407132f0287f151` |

⚠ **`git worktree prune`, a scratch purge, or `git worktree remove` on this path destroys all of
it**, and the products are gitignored so nothing else holds a copy. The directory name looks
disposable and dated; it is not. It is also NOT in the deployed checkout, which stays at
`32e403b8` because PET's array `58692544` runs from it.

**Its data inputs are symlinks into the deployed tree** — `merged`, `unfolds`,
`unfolds__SUPERSEDED_20260718`, `products/5d`, `products/4d`, `MINERvA101/opt` — linked at the
granularity where **no tracked file exists**, so the worktree's own tracked content is unaffected.
A first attempt linked the parent directories instead and `ln -sfn` nested each link *inside* the
existing directory; that is why the links are one level deeper than they look.

**The scripts for stages 4–6 are written and staged on the cluster** at the worktree root:
`sbatch_l2_debug.sh`, `l2_stages_2_to_4.sh`, `l2_stage5_assemble.sh`, `l2_stage6_measure.sh`.
⚠ Stage 6 **re-derives the graded pair's `s_proj` as a control first** and declares the
released-lateral number uninterpretable unless the control reproduces `6.145388143592225%` to
`1e-12`. Do not read a released-lateral number that comes with a failed control.
