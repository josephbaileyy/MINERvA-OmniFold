# #977 C-BKG: the composition of the paper's background template on 1A (receipt)

**What ran.** One session on login27, 2026-11-12T05:22:00Z, under the director's go for exactly
`code/cbkg_remote.sh` (d78340d2…) and `code/cbkg_fetch.sh` (ecec7721…, which pins it). 0 node-h. The inputs came
from tier3-design (2026-11-12):
- base_cv.root is MP-1 S0's unmodified-binary 1A event loop, pinned at c76256a4…
  (`measurement-paper/phase1/mp1/receipts/checks/mp1s0_base_cv_60017651.out:831`). Its mc_background is identical to
  production's 52,626 1A rows (`r4_prod_vs_base_cv.json`).
- The producer's rule is `playlist-spread-20261014/coverage/scripts/proxy_hists.py:53-54, :59`.

base_cv exists for 1A only, so this receipt covers one playlist of the twelve-playlist template.

**Fence and reads.**
- The fence was clear; only ll5d_gate_G18 and ll5d_gate_AR23 were running.
- Both inputs were sha-streamed through O_NOATIME, whole, stat unchanged and equal to their pins. uproot read through an
  O_NOATIME file object, stat unchanged.
- Log: `session/fetch.out.txt`. The verifier printed CBKG-977 OK.

**Control (passes exactly).** The producer's rule applied to base_cv: rows with sim_background_pass == 1 (52,626 of
52,626), weight w_bkg, on the 14 × 16 grid. It reproduces work_proxy's 1A__ana__B with a largest difference of
**0.0**, and Σ w = 44,360.495004 on both sides. So base_cv's mc_background is the paper's 1A template.

**Composition (members/cbkg_summary.json).** Over the 49,551 passing rows inside the grid. The weighted fractions
of the template are w_bkg sums, before POT scaling, which cancels.

| class | inner bracket (r < 850 mm) | outer bracket (r < 850·2/√3 mm) |
|---|---|---|
| out-of-phase-space signal: ν_μ CC with the truth vertex in 5980 < z < 8422 mm and inside the hexagon | 9.6 % weighted (10.6 % raw) | 32.0 % weighted (33.6 % raw) |
| genuine, ν_μ CC with the truth vertex outside the fiducial volume | 83.2 % (81.7 % raw) | 60.8 % (58.6 % raw) |
| genuine, other flavor, wrong sign or NC | 7.2 % (7.8 % raw) | 7.2 % (7.8 % raw) |

The closure genuine + out-of-phase-space = all holds to 9×10⁻¹³ under both brackets.

**Readings, not repaired:**
1. *The bracket is wide.* 22.4 % of the weight has its truth vertex between r = 850 and 981.5 mm, between the
   hexagon's inscribed and circumscribed circles. The template's out-of-phase-space share is 9.6–32.0 % (weighted).
   Narrowing it needs the analysis's own hexagon test, MAT's truth::Apothem, which this probe did not assume.
2. *Against RUN_LOG :1061's ~82 %.* That record's "Set E" is ν_μ CC failing the phase space on the truth tree, which
   includes out-of-fiducial vertices. Here ν_μ CC of any vertex is 92.8 % (weighted) of the template, and the run log's
   other 18 % (the 1,788) also holds ν_μ CC. The two are consistent; the run log does not separate out-of-fiducial
   ν_μ CC from out-of-phase-space signal.
3. *Against the publication's 0.2 %.* The other-flavor, wrong-sign and NC class is 7.2 % of the template, i.e. 0.197 %
   of the selected 1A data (the 1A template is 2.735 % of it, l_rows.json bkg_42). The publication's 8655 events
   (0.2 %) count only those components (S1). This is a descriptive coincidence of scale and was not tested. <!-- absence-ok: scopes a descriptive comparison this receipt makes; not a claim that a result does not exist -->
4. *Most of the template is genuine background by S1's definition* (other flavor or sign, NC, out-of-fiducial
   vertex): 68.0–90.4 % weighted on 1A. The out-of-phase-space signal is the remainder.

**Members:** `members/manifest.json`, `branches.json`, `cbkg_summary.json` and `cbkg_hists.npz` (the per-class 14 × 16
histograms; force-added by explicit path, *.npz being gitignored, as for pscr-20261112). The session tar (826a924f…,
20 KB) is in `session/`.
