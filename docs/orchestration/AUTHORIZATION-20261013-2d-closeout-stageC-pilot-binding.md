# AUTHORIZATION 2026-10-13 — 2D closeout: binding addendum to the Stage C pilot grant

**Issued by** the paper-tighten lane, as director. This is the binding addendum that
[`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md)
(file sha256 `136d6b49…`, §1 step 2) requires before any pilot job. With this addendum on `origin/main`, the
2d closer may deploy the package below and launch it under the grant's bounds.

**CITABLE FOR:**
- the package, the manifest, the producer and the per-job enforced worst cases that bind the pilot;
- the director's acceptance of the naming reuse in §3;
- the operating conditions in §4.

**NOT CITABLE FOR:**
- anything the pilot grant excludes. It does not raise the 12.9 node-h ceiling or change the window, order,
  stops or terminal outcomes.

## 1. Binding

| item | value |
|---|---|
| package commit | `92b0b466b4c94421446f7c751725365e8176793b` on `closeout/stagec-pilot-20261013`, base `origin/main` `ca1bb536` (ancestor verified) |
| manifest | `docs/orchestration/state/2d-closeout/stageC/pilot/manifest.json` at that commit, sha256 `39ae6ddd021ceeb843e3155182dc061abd960106f667ee1a918a20917c8a4841` |
| job table | `jobs.tsv`, sha256 `54b0abcaff3da6256c3ba791ad55ab4c95a2c5b66bb88148f82c4fa522f4b9d8` |
| producer | `2d-unfolding/unfold_2d_omnifold_unbinned.py` sha256 `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56` (`main` `ec2088a6`) |
| diagnostic copies | `driver_p1.py` `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578`; `driver_g2.py` `eb258cadfc2b0ab7191e400eb13564a2866d393e18b830c3f2d5a7d12349cc99` |
| engine | `unbinned_unfolding/python/omnifold.py` `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/` |
| review | one fresh read-only verifier: APPROVE WITH CHANGES on `0c0d4d26` (3 MATERIAL, 11 MINOR), APPROVE on `c4b8d915`, APPROVE on `92b0b466` |

Before binding, the director checked the following at the package commit:
- the manifest and `jobs.tsv` digests;
- the producer digest;
- the base ancestry;
- the scope: the package directory, plus the generated `MANIFEST.tsv` and the `verify_hash_bindings.py` 150 → 151
  binding delta;
- the gate logic of `launch.py`.

**The full commit sha the 2d closer first reported was wrong after its first eight characters.** It was
`92b0b466d4b2dce5…`, which is not a commit. The value above is `git rev-parse` of the pushed branch. Deployment
verifies that full value (§4).

## 2. Enforced worst case per job

Recomputed from `jobs.tsv` as billing × cap / 256. All jobs run on shared QOS, every cap is under 1.17 h, and
each job refuses to run unless its allocated billing equals `jobs.tsv`.

| jobs | batch | billing | cap | each (node-h) | count | subtotal |
|---|---|---|---|---|---|---|
| `2dc_C_P0_default`, `2dc_C_P0_derived` | B0 | 64 | 00:25 | 0.1042 | 2 | 0.2083 |
| `2dc_C_P2_{NormDISCC0,MaRES0,Flux23,MINOS0}` | B1 | 128 | 00:30 | 0.25 | 4 | 1.0 |
| `2dc_C_P2_MINOS0def` | B1 | 128 | 01:10 | 0.5833 | 1 | 0.5833 |
| `2dc_C_P1_unit` | B1 | 64 | 00:32 | 0.1333 | 1 | 0.1333 |
| `2dc_C_G2_on` | B2 | 128 | 00:50 | 0.4167 | 1 | 0.4167 |
| `2dc_C_G2_off_s43`, `2dc_C_G2_on_s43` (conditional) | B3 | 128 | 00:30, 00:50 | 0.25, 0.4167 | 2 | 0.6667 |
| `2dc_C_P1_{fixed,joint,bkg}_{01..20}` | B4–B7 | 64 | 00:32 | 0.1333 | 60 | 8.0 |
| `2dc_C_P3_{BeamAngleX0,MINOS0}` | B8 | 128 | 00:45 | 0.375 | 2 | 0.75 |
| **total** | | | | | **73** | **11.7583** |

- Without retries, the sum at caps is 11.7583, below the 12.9 ceiling, so the gate never refuses.
- Retries draw on the remaining 1.1417. Each retry passes through the same gate.

## 3. Naming reuse accepted

The P2-G2 universe is `Flux:23`. It was selected from inputs (`select_flux.json` `35ce6226…`): median
\|c_off − 1\| 1.775%, max 11.82%. It is also P2's Flux case, so `2dc_C_P2_Flux23` serves as P2-G2's run *a*.
The pilot grant names P2-G2 jobs `2dc_C_G2_*`, and this reuse is accepted as an exception to that naming.
P2-G2's own jobs are `2dc_C_G2_on` and the conditional `2dc_C_G2_{off,on}_s43`.

**Note for K2.** `Flux:23`'s ν-e+IMD constraint weight is ≈ 5e-5. K2 therefore measures where the mechanism
is largest, not that universe's weight in the C04-weighted band. If K2 routes MATERIAL, the director's
recommendation to Joseph states that weight.

## 4. Operating conditions

These are in addition to the grant and the DESIGN. They close two gate hazards the director found in review
that the package code does not close.

1. **The ledger's user is fixed.** `launch.py` asks `sacct` and `squeue` for `$USER`, defaulting to
   `josephrb`. A wrong user returns a header and zero rows, which the gate would read as zero charge.
   - Run every `launch.py gate|submit` as `USER=josephrb python launch.py …`.
   - Before every gate, check that the printed ledger lists every `2dc_C_*` job submitted so far.
2. **Submission lag.** A job that `squeue` lists but `sacct` does not yet list is missing from the gate's
   in-flight sum.
   - Run a gate only after every earlier submission appears in the printed ledger.
   - If one is missing, wait and re-run. Do not count it as zero.
   - Record each gate's printed arithmetic in the REPORT.
3. **The package is durable and exact.**
   - Do not force-push `closeout/stagec-pilot-20261013` or delete it before the pilot REPORT is merged.
   - Deploy by `git archive` of `92b0b466b4c94421446f7c751725365e8176793b`. Check that full sha with
     `git rev-parse` and the deployed tree against the manifest before B0.
4. **No code change after deployment.** A defect found after deployment is a stop-and-report to the
   director. A new package commit needs a new binding addendum.
