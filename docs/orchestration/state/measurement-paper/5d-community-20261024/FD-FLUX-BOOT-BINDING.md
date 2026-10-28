# Binding: 3D, the flux-correlation bootstrap over the 100 universes (2026-10-27)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` (PR #423), item 3: "3D runs: a
bootstrap of the flux correlations over the 100 universes … declared, then bound, on a login node at 0 node-h".

**Binds** [`FD-FLUX-BOOT-DECLARATION.md`](FD-FLUX-BOOT-DECLARATION.md), merged in PR #428. Its file sha256 begins
`a5166316dc66470d`.

**MEASURES:** nothing. It authorizes the declaration's deploy, its tests and its one run, at 0 node-h on a login node.

**CANNOT AUTHORIZE:**
- any change to a covariance, cell, readout or κ;
- a p value or a tail fraction;
- the new form of the paper's sensitivity sentence, which goes through the PRD read and the truth column, then to
  Joseph (decision item 3);
- a claim, a reading or printed wording, which are Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `f370da5bef042c47573a8348f51a94e43de5c432`, main after PR #428.
- `B=/pscratch/sd/j/josephrb/fd-flux-boot-20261027` and `D=$B/deploy/f370da5b`.

**The director checked,** at the pre-review head `49c20780`, the re-review head `5d16fc10` and the merged head
`e888c27f`:
- the §8 pins, all eight: `fd_flux_boot.py` `48c6eb04` (it was `33b0a709` at `49c20780`; `5d16fc10` changed only its
  docstring and the `band` label), `test_fd_flux_boot.py` `84d724ce`, `fd_g_followup.py` `ec8cbc68`, `fd_g_diag.py`
  `241bfd02`, `fd_g_compare.py` `0a3c09cd`, `s1_assemble.py` `b157250a`, `s1_assembly.json` `81e5ef3f`,
  `fd_g_readout.json` `75a9ddee`. The last six are unchanged from `main`;
- the declared test modules, locally with `-B` and a TMPDIR, at `49c20780`: 203 tests, 202 OK and one error. The error
  was `EndToEnd.test_run_as_invoked_and_recomputed_by_hand`, a 600 s subprocess timeout during a run the host slept
  through (7,392 s wall, against the lane's 77 s). Rerun alone on the awake host: `test_fd_flux_boot` **Ran 29 tests in
  18 s, OK**, and again at `5d16fc10`, **29 OK**. The timeout is a host artefact, not a defect. The cluster run in §3
  condition 1 is the gate;
- `5d16fc10`'s C_post rerun (`review/sim_followsx_target.log`), whose numbers ruling 2 uses.

## 2. Rulings on §7

1. **`correlation` is the primary variant,** as declared. `block` is the second record, with its low variance bias
   stated beside it.
2. **The band a paper sentence may describe is the percentile band, always with its offset.**
   - The declaration's own synthetic check (§4.3, after the focused re-review) shows neither band is an interval for
     the χ² under the true correlations. Against nominal 0.68, the 16–84 % percentile band covered its target in 0.37
     and 0.32 of ensembles with independent weights, and in 0.47 and 0.45 against χ²(C_post) when the weights follow
     the values; the basic band in 0.48 and 0.57, and 0.57 and 0.61.
   - The percentile band is the quantity actually measured: the scatter of Stage G's χ² over re-estimates from these
     universes. The basic band is a constructed pseudo-interval. It came closer to nominal in the toy, but stayed far
     below it, so it has no standing as an interval either, and printing it invites the interval reading. It stays in the readout as the declared companion, and is not proposed for print.
   - Any sentence says what the band is (estimation scatter given these 100 universes, under PPFX and the ν-e + IMD
     constraint), and does not call it a range for the true χ². Its wording is Joseph's.
3. **B = 2000 and seed 20261027** are accepted. The halves show the Monte Carlo error.
4. **No p value or tail fraction** is accepted, with the test that asserts it.
5. **`uniform`** is accepted as one named alternative, labelled as such.
6. **The pair stays R04–R08.** No pairs are added.
7. **`sd_over_sigma_w_root_n_eff` and `delta_method_ratio`** are descriptive, not controls, as declared.

## 3. Conditions

1. **Deploy and tests,** exactly as §2.1, with `<pin>` = `f370da5bef042c47573a8348f51a94e43de5c432`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, 0 porcelain lines before and after, the §8 digests, `tests rc=0` and
     "Ran 203 tests". Anything else is a STOP.
2. **The run,** with §2.2's argv exactly, under its 375 s timeout. Exit 0 proceeds; any other exit is a STOP, reported
   unrepaired.
3. **No step is rerun or repaired** without the director.
4. **The report is `FD-FLUX-BOOT-REPORT.md`, opened as a PR to the director.** It gives numbers only, every record with
   its label, and ruling 2 applied:
   - each band is printed with Stage G's χ̂ and the offset beside it;
   - §4.3's synthetic coverage numbers, both arms, are restated beside the bands, as the reason neither is an
     interval, and the offset is labelled the bootstrap's estimate of χ̂'s bias, its sign as measured;
   - the realized `sd_over_sigma_w_root_n_eff` is reported per cell, with the median and range.
   - The results index is regenerated in-branch under the standing ruling (a), if needed.
5. **Ledger** rows go in `fd/LEDGER.tsv`, as §9. **Retention:** `fd-flux-boot-20261027` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ. G-SENS2's α results stand.
- `docs/analysis-note/**`, including the sensitivity sentence.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
