# RC10 of the Zenodo deposit: changes B and E(a) (Joseph, 2026-11-27)

These tools build `~/codex-reports/note-measurement/zenodo-draft/package-rc10/` from RC9's package, which stays
unchanged in `package/`. The director's instruction:
- **(B)** replace the sixteen-cell C_rep with the V_F one, and change the README's definition to
  C_e^infl + C_model + C_resp + C_PL,5D;
- **(E)(a)** add regenA's 2D central values on MINERvA's published p_T edges;
- build RC10 from RC9, recomputing every value from the deposited files. Each must equal values.tex at main.

| step | tool | record |
|---|---|---|
| B: re-export `sixteen-cell/` from the V_F product `1a37b082`, with `C_e_infl.csv` added | `export_sixteen_vf.py REPO PACKAGE` | `export_sixteen_vf.log` (EXPORT B PASS) |
| E(a): `result-products-2d-published-edges/` from regenA's E (`er.root` `5171c7b8`) | `export_published_edges.py REPO PACKAGE RC9_DIR` | `export_published_edges.log` (EXPORT E(a) PASS) |
| RC10 replay tarball, from RC9's tarball plus the edited source tree, built twice | `build_rc10.py REPO RC9_TARBALL SRC WORK OUT` | `build_rc10.log` |
| clean-environment check of the whole package-rc10 (fresh venv, `env -i`, empty HOME), as for RC9 | `clean_env_check_rc10.sh PACKAGE SCRATCH` | `clean-env-rc10-steps.txt`, `verify-rc10.out.txt` |

**What changed in the replay source tree.** RC10's source tree (`zenodo-draft/work/rc10src/pkg`) is RC9's unpacked
tree with four edits and one added file:
- `expected/values.tex` is main's;
- `data/twod/result_2d_published_edges.npz` is added;
- `code/twod_numbers.py` takes `--twod-pub`, and its four per-bin comparisons with the published result
  (`\binsFive`, `\pullMean`, `\pullRMS`, `\chiPaper`) use those values;
- `code/verify_rc.py` passes `--twod-pub`;
- `README.md` describes the change.

`build_rc10.py` requires every other file to be byte-identical to RC9's.

The package's own `README.md` and `SHA256SUMS` were then edited by hand and regenerated. `../make_upload_manifest.py`
checks every RC10 item against main.
