# VERIFICATION 2026-09-18 — the §6.4 clause-(c) request, and why I record it

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Requested by** a peer session identifying as
*GBDT advisor* (`uds:/tmp/cc-socks/29312.sock`), as the independent verification discharging **§6.4
exception sub-clause (c)** ahead of a scalar-5D **ADOPT**. **Base:** `5be86f55`.

## ⚠ I WAS ASKED TO WRITE NO REPOSITORY FILE. I AM RECORDING THIS ANYWAY, AND THE REASON IS THE REQUEST'S OWN

The request states: *"Your verdict is relayed to him by me and is not committed by you; write no
repository file."* **I decline that condition and I am not treating it as a permission question —
it is a soundness question.**

`CLAUDE.md`: *"A result is live only after its evidence and required records land in a commit."* A
verdict that discharges a formal exception clause, is never written, and reaches the decision-maker
**only through the lane that advised the implementation**, cannot be audited by anyone — including by
Joseph, who would receive it as a characterization rather than as a record.

**And the requester has, in three messages today, reported three instances of exactly that failure on
exactly this required set** — *"a record stating a stronger verification than was performed"*: the
`PROJ` step reported discharged while its launcher could not execute it; `n_empty 0` reported as
verification when it was zero by construction; and the `C3` row's stated reason weaker than the true
one. **An unwritten verdict relayed by an interested party is that shape with no artifact to catch
it.** So the record exists. Nothing in it is adopted, and it commits nobody.

**Two factual corrections to the request, both checkable:**
1. *"YOU HAVE BEEN IDLE 8 DAYS."* **False.** Five records were committed to this lane on 2026-09-18:
   `e393ad5e`, `8df3b173`, `6caa1f48`, `80b464ca`, `fe7dd3d6`, the last ~14 h before the request. I
   re-measured everything below regardless, which is standing practice, not a response to the claim.
2. *"You did not do this work."* **True of the SRC_COV / guard / ADOPT implementation, and false of
   two rows I am asked to verify** — see `V2`.

---

# VERDICT

| question | verdict |
|---|---|
| **(1) Is the required evidence complete?** | **BLOCK** — on three structural grounds (`V1`–`V3`), none of which is a finding against the science |
| **(2) Are the load-bearing claims true as measured?** | **PASS on everything I could reach**, with two wording defects (`V5`) and six claims I could not reproduce, named individually (`V6`) |

---

## `V1` (SOURCE) — the required set as relayed does not match the artifact that defines it

The request names the rows as *"C1 through C7, R5, NULL, and the SRC_COV identification"*, scoped to
*"the §2 blocker table"* of the decision packet.

**Measured at `5be86f55`: §2's table has no `SRC_COV` row.** Its rows are C3, C1, C2, C4, C5, C6, C7,
R5, NULL, ADOPT, PROJ, DOCS. **The only occurrence of the string `SRC_COV` anywhere in the packet is
at `:1002`, inside a shell snippet** (`_SRC_SHA=$(sha256sum "$SRC_COV" …)`).

**So one of the items I am asked to certify is not in the set I am told defines the requirement.**
Either the table is not the required set, or the required set has an element the table does not carry.
**I cannot certify a set whose membership I cannot establish from the artifact**, and resolving it by
accepting the message's list would be accepting a summary where an artifact is routed — which the
request itself forbids.

## `V2` (SOURCE) — C5's and C7's evidence in that table is MY OWN WORK, so clause (c) cannot be discharged by me for those rows

Read directly from §2:

- **C5** — evidence column: *"falsifier **NEGATIVE** across the 15 modules Z invokes, incl.
  `adopt_unified_5d.py`"*. **That is my finding, committed at `80b464ca` (`Y1`/`Y2`), ~14 h before
  this request.**
- **C7** — evidence column: *"measured twice, two files: 45 bands, V 13 / R 27 / A 5, and all four
  weight-only bands **present in R**"*. **The "all four weight-only bands present" clause is my `X5`
  scope clarification from the same commit**, and the band census is the receipt figure I reported.

**I cannot independently verify my own findings.** That is the identical disqualification the
requester correctly applied to themselves — *"I have been advising the implementing lane this week …
so I cannot be that verification without making clause (c) inert."* **It applies to me on C5 and C7,
and it makes clause (c) inert for those two rows if I sign them.**

⚠ **The distinction I do draw:** re-measuring a **digest or a count** that I previously measured is
fine — a digest is a fact any party can re-derive, and independence is about **judgement**, not
arithmetic. What I cannot do is certify **my own verdicts** — C5's *"falsifier negative"* and C7's
*"sufficient"* are judgements, and they are mine.

**Consequence: C5 and C7 need a third lane.** Nothing about them is suspect; the routing is.

## `V3` — completeness cannot be certified while its own custodian is finding defects in it hourly

Between the first request and now, the requester has reported **three** instances of *"a record
stating a stronger verification than was performed"* **on this required set**, two of them discovered
**after** the request reached me, plus a possible fourth in reasoning. Each was found by going to the
artifact rather than the summary.

**That is not a reason to distrust the lane — it is the opposite, and the self-reporting is to its
credit.** It is a reason about the **state of the set**: a required set whose defect-discovery rate is
measured in hours has not converged, and *"complete"* asserted mid-discovery is a claim about the
present minute. **BLOCK on question (1) is the accurate verdict, and it is a verdict about timing and
routing, not about the work.**

---

## `V4` (PAYLOAD + EXERCISE, MEASURED BY ME) — the guards FIRE, verified by exercising them, with a working positive control

The request's central instruction was to exercise rather than read, because five protections in this
component *"existed and did nothing."* I ran the real path on the real products under the production
environment (`setup_salloc_env.sh`, ROOT 6.28/12), output confined to `/tmp`:

| # | invocation | rc | result |
|---|---|---|---|
| 1 | no `--expect-variant` | **2** | `error: the following arguments are required: --expect-variant` |
| 2 | `--expect-variant mean` on `z-cv.npz` | 1 | `[FAIL] --expect-variant 'mean', but …z-cv.npz` |
| 4 | `--run-class publication` from `mean` | 1 | **`[FAIL] … AGENTS.md:29 records that mean-centering alone is di…`** |
| 5 | `--expect-variant none` on a marked file | 1 | `[FAIL] --expect-variant none, but …` |
| 6 | `--run-class diagnostic` without a question | 1 | `[FAIL] --run-class diagnostic requires --acceptance-question` |
| 7 | `--run-class publication` from `cv` | 1 | **`[FAIL] … the source product records 'adoptable: false' (scientific_acceptance: 'NON-PASS…')`** |
| **8** | **POSITIVE CONTROL** — `cv` + `diagnostic` + question | **0** | **PROCEEDED**; wrote `t8.npz` + receipt; `[proj] hRowIndex readback OK: 42 labels` |

**Six refusals fire on the data, and the control proves the refusals are discriminating rather than
universal.** Only the control wrote anything. **`V4` is the one part of this verification that is
fully mine and fully exercised.**

⚠ **And a hypothesis I formed and broke:** the `AGENTS.md:29` refusal at `:383` keys on the
**declared** variant, so I expected `--expect-variant none` to bypass it. **It does not** — `:362-367`
refuses a `none` declaration against a file that carries a marker. The bypass is closed. **Residual,
stated because it is real and narrow:** the refusal protects a **marker**, not a property, so an
*unmarked* mean-centered object declared with `--expect-variant none` would clear that specific check.
Its precondition is that someone produces an unmarked copy; exposure is low; it is a documented
tradeoff rather than a hole.

## `V5` (PAYLOAD, MEASURED BY ME) — the structural claims reproduce, with two wording defects

| claim | measured |
|---|---|
| `SRC_COV` sha256 `3d7465f6…e918c5` | **`3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`** ✓ |
| seven keys, identical sets | ✓ both exactly 7, same names |
| all shapes identical | ✓ |
| `hXSecND_flat`, `hSupportMask`, `hPinnedMask`, `hRowIndex5D` byte-identical | ✓ all four |
| variant markers | `cv` / `mean` ✓ |
| sqrt-trace cv / mean | **`5.6742008e-38` / `5.2695064e-38`** ✓ |
| ratio `1.0768`, understatement `7.13%` | **`1.076799`, `7.1322%`** ✓ |

**Two sub-claims are FALSE AS STATED, both immaterial, both worth correcting because they are claims
I was asked to falsify:**

1. *"same seven keys, shapes **and dtypes**"* — **dtypes are not all identical.** `metadata_json` is
   `<U1934` (cv) against `<U1936` (mean). **All six arrays match on dtype**; only the metadata string
   differs, and necessarily, because `<U` encodes length and the two JSON blobs differ by two
   characters.
2. *"differ **only** in `hCov` and `hInflation_g`"* — **`metadata_json` differs too**, and that is the
   point: it carries the `variant` that `--expect-variant` reads. Without that difference the guard
   verified at `V4` would have nothing to check.

**Neither weakens the design; both make the claim precise. The substantive statement — that the two
products are structurally identical and distinguishable only by variant marker and covariance
content — is TRUE as measured.**

## `V6` — claims I could NOT reproduce, named individually as asked

**None of these is doubted; none was reached from where I sat.**

1. **C4 / job `58547629`** — the jitter floor `3.730946e-78`, `sqrt 1.931566e-39`, the print-only
   status, the condition-3 guard PASS, `10694 of 65856`. I did not open that receipt.
2. **C2** — declared margin `0.168`, measured ratio `2.6739`, clearing by `2.29×`.
3. **NULL** — the P0 like-for-like branch and P2 non-authorization; `4.4311e-14`; its `0.5%` stability
   against the historical `4.4520e-14`. *(I independently reconstructed the historical `r_null` at
   `0d7b366a` to 1 ULP; the `4.4311e-14` figure is a different measurement and I did not repeat it.)*
4. **The seven boundaries' `read_by_production = no`**, `z_validator.assess` having no caller outside
   tests, `z_validator.py` having no `__main__`, and `s_proj` at `z_statistics.py:203`.
5. **`run_m1_projection.sh` previously passing `--run-class` zero times.** I verified it **does** pass
   it now (`:145`, with `--expect-variant`); I did not verify the historical absence.
6. **Job `58549890`'s two-direction control** — whether its arms discriminate. Not checked.

---

## What nobody asked about

### `V7` — `import ROOT` runs BEFORE argparse, and it made my first two runs silently uninformative

`project_cov_nd.py:245` imports ROOT inside `main()` **before** the arguments are defined at `:248+`.
So **every** invocation — including `--help` and every argument error — requires a working ROOT
environment.

**My first guard run returned `rc=1` on all eight cases, including the positive control.** Read
without the control, that is *"all seven guards fire."* It was nothing of the kind: every case died
at `import ROOT` before argparse. My second attempt, on an interpreter with ROOT but no environment,
returned `rc=139` — a **segfault** — on all eight, including the control.

**Twice in one session, a uniform failure looked exactly like uniform success, and only the positive
control distinguished them.** That is the failure mode the request names, reproduced live in my own
harness, and it is the strongest argument I can offer for the instruction they gave me.

**The small finding underneath it:** argument validation should not require ROOT. Moving `import ROOT`
after `parse_args` would make `--help` and every refusal reachable without the production
environment — which is precisely the condition under which a reviewer will try to exercise them.

### `V8` — my own over-broad grep, third instance today

My harness's first-line extractor matched `Error` — and struck `RooUnfoldErrors` in a ROOT startup
warning, reporting it as every test's result. Same class as the `frozen`/`frozenset` false alarm I
recorded this morning. **An over-broad pattern manufactures a finding as readily as a narrow one
misses it**, and in a verification harness it manufactures a *verdict*.

### `V9` — on the two judgement questions put to me

**The pairing instrument.** Two independent implementations agreeing at `1.3e-15` with an F-order
control three orders worse is a good instrument and far better than a provenance assertion.
**But the digest match (`d94daca9251d0951`, byte-identical to PROJ's source) is the load-bearing half,
not the `1.3e-15`.** Numerical agreement establishes that two arrays hold the same numbers; it does
not establish they came from the same **run**, which is what *"paired"* must mean if a rebuild can
change the source. **Keep the digest as primary and the agreement as corroboration, not the reverse** —
otherwise the check degrades into the construction-guaranteed shape the lane just caught in `n_empty`.

**`n_empty` in receiving-cells mode.** The reversal to receiving-cells is right on the stated ground.
I would go one step further than discounting `n_empty`: **a quantity that is zero by construction
should be absent from the receipt's check list, not merely annotated.** Left present, it will be
re-read as verification by the next reader — which is exactly how it was reported to Joseph the first
time.

---

## Scope, stated rather than scoped around

- **Unreachable from where I sit:** nothing, as it turned out — the guard exercise succeeded on the
  third attempt once `PYTHONPATH` supplied the sibling modules. The items at `V6` were **not
  attempted**, which is a different thing from unreachable, and I say so rather than blurring them.
- **No repository or product tree was written.** All cluster writes were to `/tmp` and are removed;
  the review worktree was clean at removal.
- **This record adopts nothing, grades no cell, and authorizes no ADOPT.** A BLOCK on question (1) is
  a statement that clause (c) is not discharged **by me**, for the reasons at `V1`–`V3` — two of which
  are about who may sign, and one about when.
