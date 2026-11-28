# V_F Phase 2: FOLLOWUPS (non-blocking under the director's scope rulings, 2026-11-26)

The readings are final at #1368 under the director's last ruling: round 3 is the last read of this diff. Only a missed
unruled weakening in the present OLD -> V_F data, or a wrong recomputed value, would block.

Round 3 (`reads/p2-fix3-codex-gpt-6.2-sol.txt`) found neither. The present sweep holds exactly four control D events,
each under its named ruling. No structural leaf changes, the tool exits 0, and the values, moved keys, guards and
decision rules equal those of the last three heads.

The classifier gaps below would matter only for a future rerun with different data:

1. **X `named`: a flagged quadrant can be replaced by "joint".** When the joint p is already below 0.05 and a
   quadrant clears, fd_xcov's X rule sets `named` from ["QA"] to ["joint"]. The sweep reads "joint" as a new flag,
   which is a false STOP. Fix: treat `named` as an outcome on the X scale (quadrant-named differ, then joint differ,
   then agree), not as a flag list.
2. **RSN WR verdict: no scale for the WR prose verdict.** A W2 -> W1 improvement (rsn_read.py:213-216) changes the
   verdict string, and that change is an event, a false STOP. Fix: order the WR verdict by its W class and the
   material list.
3. **V-ATLAS: a cell becoming valid adds contrasts.** `n_contrasts`, `pair` and `axes` are structural, so a validity
   gain gives a false STOP. Fix: classify them as descriptive under valid_region's contrast records.
4. **The QD ruling's premise.** The premise bounds V_F rho* to (0.999, 1) but leaves OLD rho* unbounded above, so a
   crossing from 1.2475 would pass. The ruled values are OLD 1.00353 (cr) and 1.00349 (gover). Fix: also bound OLD
   rho* (for example, below 1.01) or pin the two ruled pairs.
5. **`mode` is descriptive, but G-SENS2's H2 compares it for equality.** H2 is a producer control (fd_g_followup.py:650)
   that refuses with exit 1, so a V_F readout exists only if H2 passed. Both V_F sens2 readouts list H2 in
   `controls_passed`, which is swept. Fix: none needed while H2 stays a refusing control. Note it if H2 ever becomes a
   recorded reading.

## Earlier Phase 2 FOLLOWUPS

- **xk's CR_G2R substitute** is p2_overlap("cr")'s record without `vf_data_product_sha256`. K reads only `quadrants`,
  which are value-identical. See P2-RECEIPT.md.
- **`test_prr.py::test_the_floor_seeds_are_no_campaigns`** fails on newer campaigns' files. It is a bound file and was
  not touched.
- **Fetch-tool reads.** The malformed-archive constructions and the same-account TOCTOU race were ruled non-blocking
  in FD-VF-BINDING-2b.
- **prr's f-equality assert** is not reached by an offline test. A fetch rerun with a perturbed product would reach
  it.
