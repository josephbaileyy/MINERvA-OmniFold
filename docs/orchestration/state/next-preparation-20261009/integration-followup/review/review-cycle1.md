# Focused re-review: follow-up integration repair batch `ae0bfb76..1a7ef7bc`

| field | value |
|---|---|
| Reviewer | the same fresh read-only Claude subagent (Claude Opus 5.5) as the initial review. This is its one allowed focused re-review |
| Fixed commit | `1a7ef7bc0594e4411c084993a91096b843bd18bf`. The repair batch is one commit on top of `ae0bfb76` |
| Time | 2026-10-10T18:07:57Z to about 18:12Z |
| CPU | about 0.01 core-h. The manifest checks, index check, lint and hash bindings took about 15 s user+sys in total; the rest was git and greps. One thread per command |
| Worktree | `scratchpad/fu/review-wt2`, detached at `1a7ef7bc`. Start: `--porcelain --untracked-files=all` 0 lines, `--ignored` 0 lines. End: `--untracked-files=all` 0 lines; `--ignored` 2 lines, `docs/orchestration/state/__pycache__/` and `lib/__pycache__/` from the check scripts. Removed afterwards with `git worktree remove --force` |
| Tripwire `hits.log` | absent (0 lines) at start and at end |

## Verdict: **PASS**

Every finding F1–F9 is resolved, as its disposition in REPORT §9 states. The pin and the manifest
digest still hold. My preserved review is byte-identical to what I wrote, and every shared check
passes.

One new NOTE (R1): the §4.4 disclosure explains the calls 2–5 case with the wrong mechanism. Its
conclusion, its bound and its operator rule are correct. R1 does not block landing.

## Per-finding status

| # | status | evidence |
|---|---|---|
| F1 | **RESOLVED** | The CATALOG D-ID row (`CATALOG.md:85`) now reads "binned, signal-only, simulation-only diagnostic on development truths, and it validates no interval; its outcome and limits are in its own report". It names no branch outcome. A grep for `branch C` / `branch **C` over `KNOWN_ISSUES.md`, `CATALOG.md`, `docs/OPEN_ITEMS.md`, `AGENTS.md` and `docs/CURRENT_WORK.md` finds nothing. REPORT §7's sentence (`:299`) is now true at the fixed commit |
| F2 | **RESOLVED** | `two-d-path/REPORT.md` §10's dated correction now adds: "§3.6 compares two LightGBM sweeps. It shows that cross-sweep delta scatter exists for LightGBM; no between-estimator scatter has been measured (follow-up review F2)". It stays inside the italic dated correction. The lane's sentence and the preserved reviews are untouched |
| F3 | **RESOLVED (disclosed)**, with R1 | §4.4 and the §8 row "SB1 operator caveats". Most of the description is accurate: the queued-then-unparseable or non-zero-after-queue case, the id never being set, `on_error` being unable to cancel it, my measurement, a lone hash job possible at call 1 (H0) or call 6 (H1), the `squeue --me --name=sb1_H0,…,sb1_H1` rule after any non-zero exit, and the charge counted against the 2.0 node-h. **Bound checked:** in `launch/launch-spec.json`, H0 and H1 are each `shared`, 2 CPUs, 45 min, which gives 2/256 × 0.75 = **0.00586 node-h**. That matches the SB1 job table (`sb1-prep/REPORT.md:351,356`: 0.0059 each), `sb1_hash.sbatch` (`--qos=shared`, `--cpus-per-task=2`, `--time=00:45:00`) and `sb1_submit.sh:65,74` (`--time=00:45:00`). Submission stops at the first failure, so at most one orphan exists. The planned ceilings sum to 1.6992, and 1.6992 + 0.0059 is still under the 2.0 cap. The mechanism sentence for calls 2–5 is wrong: see R1 |
| F4 | **RESOLVED (disclosed)** | §4.4 and §8 say the older SB1 pin wording (§7.2 opening, §16) is superseded and that quoting `b7c951b3` fails closed. P is not edited, which keeps the pin |
| F5 | **RESOLVED (disclosed)** | §4.4 states the rule exactly: "any ancestor of HEAD whose P, executed modules and guard are byte-equal to HEAD's", including the merge commit. It also says an authorization should still quote `d4335d3b` |
| F6 | **RESOLVED (disclosed)** | §4.4 states the check-to-source window, that the digest covers only the top-level setup file, and that receipts record the submission-time digest |
| F7 | **RESOLVED** | The wording is now "offset c … (x_u^X = x_u^L + c for every universe and the CV) shifts both centrals apart by c and cancels in every delta". It is correct and unambiguous |
| F8 | **RESOLVED** | CATALOG now says the reports "land on `main` together through this integration". KI-88 and the CATALOG 2D row now say "303–1,131 admitted node-h at the declared tier (149–570 for the narrower regional alternative)". Checked against `two-d-path/design_arith.json` `costs.full_route_admitted`: L42 declared_family 302.88 / 1,130.78, regional 149.45 / 570.02. "Narrower alternative" is the lane's own wording (`two-d-path/REPORT.md:114,359,685`). The KI-88 row stays OPEN and carries no label |
| F9 | **RESOLVED** | The §4.3 column now reads "tree `dcae1a3a` (`P` identical to the pin `d4335d3b`)" |

## New finding

| id | severity | file:line | finding | suggested repair |
|---|---|---|---|---|
| R1 | NOTE | `Q/integration-followup/REPORT.md:186-187` (§4.4, F3 bullet 2) | The text says that at calls 2–5 `--kill-on-invalid-dep=yes` removes the orphan "because its dependency names an id that does not exist". That is not the mechanism. Job k's `afterok` names job k−1, whose id was parsed and set and does exist. `on_error` cancels job k−1, so the dependency can never be satisfied, and that is what makes Slurm remove the orphan. The conclusion is right in practice: job k−1 cannot have completed within the seconds the submission takes, since H0 alone hashes about 171 GB. The bound and the operator rule do not depend on this sentence. | Replace it with "because `on_error` cancels the job its `afterok` names, so the dependency can never be satisfied" |

## The other required checks

- **(2) Pin.**
  - `git diff --name-only d4335d3b 1a7ef7bc -- Q/sb1-prep <24 manifest modules + guard paths>`: empty.
  - sha256 of `P/manifest/expected-code.json` at `1a7ef7bc`: `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a`.
  - The pin `d4335d3b` and the digest stand.
- **(3) Preserved review.** `cmp Q/integration-followup/review/review.md <scratch>/fu/review-scratch/review.md` gives IDENTICAL. Its sha256 is `9c490054c79e376984ac703f4e914d63229e52876c2355bf26a9bfa630d2baa0`, which matches §9's `9c490054…`. It has a `MACHINE` row in the regenerated `MANIFEST.tsv`.
- **(4) Shared checks.**

  | check | result |
  |---|---|
  | `generate_manifest.py --check --at-sha HEAD` | OK (rows 2,039, `unused_overrides=2`, the two intended pre-registrations) |
  | `generate_manifest.py --check` | OK, `tree=clean` |
  | `live_doc_indexed.py --unrowed` | 0 |
  | `control_plane_lint.py` | CONTROL-PLANE PASS |
  | `verify_hash_bindings.py` | ALL BINDINGS INTACT |

  None of them modified the tree.
- **(5) Scope and overclaim.**
  - The repair commit touches only six files: `KNOWN_ISSUES.md` row 88, `CATALOG.md`, the generated `MANIFEST.tsv`, the integration REPORT, the new preserved `review/review.md`, and the dated correction in `two-d-path/REPORT.md` §10. All six are inside the owner's scope.
  - Nothing changed under P, in publication sources (empty diff against `a16d5786`), in the preserved lane reviews, or in any driver or helper.
  - §9 describes my review accurately: setup, independent checks, 0 MATERIAL / 3 MINOR / 6 NOTE. It labels the repair batch as awaiting this re-review.
  - The new §8 rows add caveats and context and grant no authority.
  - No new overclaim, apart from R1's mechanism wording.
