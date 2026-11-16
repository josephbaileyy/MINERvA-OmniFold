# cr: fd_gencmp cmd_overlap re-run on route A's Q_R (package; DRAFT for the director and coverage-5b-audit)

The director's XCOV ruling: after the RE-2-shapes production (#1167), re-run fd_gencmp cmd_overlap under C_new.
GENCMP amendment E step C-R ran `fd_gencmp.py overlap --arm refined` on partc-r2's Q_R (fd/gencmp-e/c-r/e_cr.sh,
readout overlap_refined.json). cr runs the same command with route A's Q_R, `cov2d-re2shapes-20261115/g2r/
combination/s5_plus_playlist.npz` (81fdd16f), pinned by `INPUTS-g2r.sha256`, beside step C-R's two INPUTS files.
The connect (`connect-g2r-cr.sh`, sent by sha; not in this commit because it pins this commit) first reruns step C-R
exactly, as a control: `cr_compare.py` requires its readout to equal the committed one after dropping argv and the
deploy prefix. Only on PASS does it run the g2r arm.

At main d58d0d18, the four code files the readout records (fd_gencmp.py 4ebaa7cb, fd_g_compare.py 0a3c09cd,
s1_assemble.py b157250a, s5p_stage1_inspect.py 26569afc) and its four deploy-relative inputs equal step C-R's.

| file | what |
|---|---|
| `INPUTS-g2r.sha256` | the pin of route A's Q_R |
| `cr_compare.py`, `test_cr_compare.py` (+ `.out.txt`) | the control's comparison: moved deploy and argv PASS; a reading, an input digest, atime_unchanged, an extra key or code_sha256 each STOP |

**CANNOT AUTHORIZE:** any reading of the agree/differ outcomes or any wording. The director takes them.
