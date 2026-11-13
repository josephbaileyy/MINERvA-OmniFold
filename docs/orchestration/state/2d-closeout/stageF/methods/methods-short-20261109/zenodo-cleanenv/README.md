# D6 clean-environment test of the result package (#981), with a claim map against #977 (2026-11-13)

**By** the valid-region lane (director-helper-2), for the director and limitation-resolver, who owns #981's re-pin.

**Under** Joseph's D6 (`DECISION-20261112-joseph-consult-d1-d7.md:47-49`): before the Zenodo deposit, the package is
tested from a clean environment, and each headline claim is mapped to what reproduces it.

**Scope:** read-only, local, 0 node-h. Neither #981 nor #977 was edited. The deposit still needs Joseph's final go on
its contents (D6).

**The heads tested:**
- **#981:** `pkg/methods-result-20261109` at `91f9cb615dfe3a19ec20150627d28419d2daafd8`. limitation-resolver confirmed it
  is the head to test and that the re-pin has not started.
- **#977:** `draft/methods-short-20261109` at `a871379960f2681b37dd98cfd7ab63562d1dae9f`, its head when the claim map
  was made.
- **main:** `1099f8b35`, which holds the re-pin list `repin/repin_list.tsv` (30 rows, digest `b16ccb4d`).

## The result

**The documented commands pass in a clean environment.**
- `build_package.py --check` passes. Its line is "RESULT-PACKAGE :: PASS (29 files equal a rebuild; 985 values
  checked) :: INCOMPLETE, pending: ENS1, FD-PRR, LL5D, V-HALF" (`runs/runcheck.out.txt:1`).
- `--self-test` passes (`runs/runself-test.out.txt`, last line).
- SHA256SUMS verifies 30 of 30 (`runs/sha256sums.out.txt`).
- The setup was a fresh clone in a new empty directory, a fresh venv holding only pip (the README states "Python 3,
  standard library only"), `env -i` and an empty HOME.
- The checkout was clean afterwards: `git status --porcelain` printed 0 lines.

**The structural gaps for a deposit (S1–S6 below):**
- The rebuild needs the `git` executable and a full repository history that contains PAPER_REF. It fails in a
  single-branch clone of the package and in a tree without `.git`, the form a GitHub-release archive takes.
- It needs Python ≥ 3.12, which the README doesn't say. Python 3.9.6 fails.
- One re-pin item is not on the list: the tune-name keys.

**The claim map (below):**
- The package regenerates the fake-data tests, the tunes, the 16-cell result and its covariances, the validity
  classes, and the 2D benchmark's integral, χ² and arrays.
- The package holds nothing for these headline claims:
  - the coverage results;
  - the stability numbers;
  - the RSN sensitivities;
  - the background composition;
  - the prior-retention (FD-PRR) results;
  - both algorithm-dependence results.
- Each of those is regenerated instead by the paper's own `make_values_fived16.py --check` from sha-pinned committed
  readouts. That passes in the same clean venv at #977's head (4258 values; `runs/mv977check.out.txt:1`).
- **No route at all:**
  - the LL5D five-observable coverage result, still `\fvpending` at #977's head;
  - five unkeyed literals: Table 1's T = 382.8 and 138.5, and §6.1's 0.23 %, 0.37 % and 2.5.

## The commands (`runs/rc.tsv`; each rc read unpiped)

| step | layout | python | command | rc | real (s) |
|---|---|---|---|---|---|
| clone | new empty dir | – | `git clone --branch pkg/methods-result-20261109 <origin>` | 0 | 74.92 |
| A1 | full clone | 3.12.2 venv | `build_package.py --check` (the README's command, from the repo root) | 0 | 0.74 |
| A2 | full clone | 3.12.2 venv | `build_package.py --self-test` | 0 | 2.79 |
| A3 | full clone | – | `shasum -a 256 -c SHA256SUMS` | 0, 30 OK | – |
| A4 | full clone | – | `receipts/c2a-20261109`: `shasum -a 256 -c SHA256SUMS.txt` | 0, 15 OK | – |
| B1 | single-branch clone | 3.12.2 venv | `--check` | **1** | – |
| B2 | `git archive` tree, no `.git` | 3.12.2 venv | `--check` | **1** | – |
| B3 | `git archive` tree | – | `shasum -a 256 -c SHA256SUMS` | 0, 30 OK | – |
| C1, C2 | full clone | **3.9.6** venv | `--check`, `--self-test` | **1, 1** | 0.25, 0.11 |
| C3, C4 | full clone | 3.13.7, 3.14.6 venvs | `--check` | 0, 0 | – |
| D1, D2 | worktree at #977 a8713799 | 3.12.2 venv | `make_values_fived16.py --check`, `--self-test` | 0, 0 | 0.49, 3.56 |
| D3 | – | 3.12.2 venv | main's `repin_check.py a8713799…` | 0, PASS 30 rows | – |

- The interpreters were the venvs of `/Users/josephbailey/miniconda3` (3.12.2), `/usr/bin/python3` (3.9.6) and
  Homebrew's 3.13 and 3.14.
- git was `2.39.3 (Apple Git-146)`.
- Every run used `env -i PATH=<venv>/bin:/usr/bin:/bin HOME=<empty>`.

## Structural findings, for the re-pin (S1–S6)

**S1. The rebuild depends on git and on PAPER_REF being in the clone's history.**
- `build_package.py:41-42`@91f9cb615 exits unless it runs inside a git checkout.
- `at_ref` (`:195-197`) reads the paper with `git show 5c8f0d7a…:<path>`.
- PAPER_REF `5c8f0d7a` is an ancestor of neither 91f9cb615 nor origin/main. Only `draft/methods-short-20261109` and
  eight `figures/methods-*` branches contain it.
- **The single-branch clone (B1)** fails: "cannot read docs/analysis-note/paper_body.tex at 5c8f0d7a…"
  (`runs/sb-check.out.txt:1`).
- **The tree without `.git` (B2)** fails: "not inside a git checkout; the build reads the paper at PAPER_REF through
  git" (`runs/tar-check.err.txt:1`). That is the form Zenodo's GitHub integration archives.
- In B2 only `shasum -c` still works (B3).
- **What the re-pin changes:** re-pinning to #977's merged head on main puts PAPER_REF into main's history, which fixes
  B1 for a full clone of main. It does not fix B2.
- **A decision for the director, Joseph and limitation-resolver:** what the deposit contains, and how the deposited
  copy is checked. For example, a mode that reads the paper files from the deposited tree, or a deposit that carries
  the history.

**S2. An unlisted dependency.**
- The README says "Python 3, standard library only" (`README.txt:349`@91f9cb615).
- The build also needs the `git` executable.
- It needs the source repository outside the package directory. It imports `docs/analysis-note/make_values_fived16.py`
  and reads `values_fived16.tex`, `values.tex` and the sha-pinned records in `SOURCES`.
- The README's "From the root of the source repository" says this, but the deposit must then carry that repository.

**S3. The minimum Python is unstated.**
- `docs/analysis-note/make_values_fived16.py:1435`@91f9cb615 nests double quotes inside a double-quoted f-string, which
  parses only from Python 3.12 (PEP 701).
- At #977 a8713799 the same construct is at `make_values_fived16.py:2634,2638`, and py3.9 fails to parse that file
  too.
- Both commands fail on 3.9.6 with `SyntaxError: f-string: unmatched '('` (`runs/py39check.err.txt:14-17`).
- 3.12.2, 3.13.7 and 3.14.6 pass.
- `build_package.py` itself parses on 3.9.
- 3.10 and 3.11 were not available here and were not measured.
  <!-- absence-ok: this run's own scope; no 3.10 or 3.11 interpreter is installed on this machine (ls /opt/homebrew/bin/python3.1* /usr/local/bin/python3.1* lists only 3.12, 3.13, 3.13t and 3.14, with their intel64 builds) -->

**S4. Checksum coverage.**
- SHA256SUMS lists 30 files: README, PROVENANCE, the build and the package files.
- `receipts/c2a-20261109/` has its own `SHA256SUMS.txt`, and 15 of 15 verify.
- The two files in `connect/` are in neither.
- `connect/cov2d_arrays_login.sh` names cluster paths on 2 lines. It is the provenance of the 2D transcription, not a
  documented command. The 2D arrays' first link, `cov2d_Q_205.npz` (`7153b194`), is never committed, by the director's
  ruling, so the package's route for the arrays is the CSV transcription and its receipt.

**S5. NEW for the re-pin, not on the list: the tune-name keys.**
- At #977, `\fvval{f1-tune-g18}` and `\fvval{f1-tune-ar23}` are `\mbox{G18\_10a\_02\_11b}` and
  `\mbox{AR23\_20i\_00\_000}` (`values_fived16.tex:2072,2076`@a8713799). The wrap entered at 10b88ad9b.
- `build_tunes` builds the unwrapped form: `build_package.py:397`@91f9cb615,
  `gen.removeprefix("genie_v3_").replace("_", r"\_")`.
- So once #981 takes main, `c.key` refuses `sec-fd16_tunes.csv` (`runs/checks-vs-head.txt:2-3`).
- The dry runs could not show this, because before the merge the build reads `values_fived16.tex` from #981's own tree.
- Search: `grep -nE 'f1-tune|mbox|build_tunes|B397' repin_list.tsv` (main's, digest b16ccb4d) returns rc 1. No open
  PR adds re-pin rows: `gh pr list --state open` has no branch matching `981|repin`.

**S6. The other stale checks are all on the list.**
- `tools/compare_head.py` compares the 895 checks the build makes (`runs/checks.tsv`, logged by `tools/log_checks.py`)
  with #977 a8713799.
- 886 still hold. 2 are S5. The other 7 are on the list:
  - RP16, "each leave 14 …";
  - RP13, "Fourteen cells … R02 and R06 fail";
  - RP15, the three V-PRIOR lines;
  - RP22, Table 1's "Integral ratio … descriptive";
  - RP09, "The smallest change resolved …".
- `repin_check.py` passes all 30 rows at a8713799 (`runs/repin-a8713799.txt`).
- Every label #981 binds is present once at a8713799, `tab:gen16` among them. So limitation-resolver's stop item for
  Table S14 does not fire at this head.

## The claim map (#977 a8713799)

**The routes:**
- **P, the package regenerates it.** A package file is rebuilt byte for byte by `build_package.py --check` from
  sha-pinned committed records, and its value is checked against the printed one. This is a transcription: the README
  says the build "recomputes no physics".
- **V, an archived product with provenance.** The value is not in the package. The paper's own
  `make_values_fived16.py --check` at #977 regenerates it from the readout it pins by sha256. That ran in the clean
  venv (D1).
- **L, a literal in the tex that neither builder checks.**
- **N, nothing,** pending or without a record.

Readout pins are the first 8 hex of the sha256 that `make_values_fived16.py` asserts (`READOUTS`). Keys are mapped to
readouts through the function that assigns them; the readouts below are the ones that function reads.

| claim at #977 a8713799 | where | key or literal | route |
|---|---|---|---|
| **Abstract:** "reproduces the published integral within about 1%" | main_paper; paper_body:231,273 | `\ratioTot` = 1.010 | **P**: `sec-repro2d_benchmark.csv` (macro check) |
| **Abstract:** "but shows a shape difference" (normalization χ² 0.04 against 465; 73 and 139 directions give 136 and 285; condition number 1.5×10¹²) | paper_body:276,278 | printed literals | **P**: `sec-repro2d_benchmark.csv` (5 printed-phrase checks; 2 move, RP09/RP22) |
| benchmark χ²/ndf | paper_body:231,276 | `\chiPaper` = 2.27 | **P** (macro check) |
| **Abstract:** OmniFold differs from binned IBU beyond paired noise | paper_body:289 | `c2c1-T` 382.8, `c2c1-max` 138.5, `c2c1-dibu`, `c2c1-der` | **V**: c2c1 `fd/receipts-ref-c2c1/step2/read-2/readout.json` 0ee21301 |
| the same T and null maximum in Table 1 | paper_body:232 | literals `T=382.8`, `138.5` | **L**: equal to the keyed values in §4.2 today, with no check |
| **Abstract:** retains part of its prior; some cells move opposite | paper_body:418-419 (sec:prr) | `prr-*` | **V**: prr `fd/receipts-prr/read/cluster/readout.json` 9238f22b. The package has `pending/FD-PRR.txt` only |
| **Abstract:** noise-free, IBU overshoots along the prior-to-truth direction | paper_body:436 | `prr-cmp-*`, verdict `prr-abs` | **V**: prr 9238f22b |
| **Abstract:** fake-data bias at the GiBUU hybrid and q3 tilt | paper_body:212,237,357; tab:fd16 | `f0b-*` | **P**: `tab-fd16.csv` (216 checks). **V**: f0b `fd/with-cpl/readout/fd_f0b_readout.json` 5f542830 |
| held-out tunes pass the bias criteria | paper_body:238,402 | `f1-g18-chi2int` 9, `f1-ar23-chi2int` 14 | **P**: `sec-fd16_tunes.csv` (26 checks; S5 at the re-pin). **V**: f1 5ccc89e5 |
| **Abstract:** sensitive to rounding-level changes, beyond the requirement | paper_body:244,514 | `s5e-round-median` 0.8, `s5e-round-max` 2.6 | **V**: s5e `state/s5e/cand/assess_receipt.json` 84266e30 |
| the same section's 0.23 % (median per joint cell), 0.37 % (bootstrap σ) and "up to 2.5" (lower-capacity variant) | paper_body:514 | literals | **L**: no key. Not recomputed here |
| ENS1: meets the requirement, worse at 1 of 17 truths, not adopted | paper_body:544; supp:823 | `ens1-*` | **V**: ens1s1 7f5a9ce4, ens1s2 c2ee701d. The package has `pending/ENS1.txt` (RP23 is the keys row) |
| **Abstract:** the 2D covariance rebuilt at two tunes under-covers at both (0 of 300 in the joint region, against 207.6 expected at AR23; mean χ²/ndf 16.55 and 24.17) | paper_body:566,579 | `cov2d-*` | **V**: cov2dar23 fe5263e9, cov2dg18 84976694, nulls 80274e52 and 6bd5259d. In the package only as README scope text |
| where the 2D χ² sits (eigenbasis decomposition) | paper_body:601; supp:1005 | `t2a-*` | **V**: t2aar23 33b7fd40, t2ag18 6757055e |
| **Abstract:** the reported five-observable intervals lack validated coverage | main_paper (RP06); paper_body:550 (sec:ll5d) | the LL5D result is `\fvpending`, and Table 1's row is empty | **N**: pending. The package has `pending/LL5D.txt` |
| **Abstract:** on data, the 16 cells depend on the algorithm (T = 194.4 against 28.12 and 39.04; R11 +20.7 %, R06 −18.1 %, R05 +11.5 %) | paper_body:493ff (sec:ibu) | `ibu16-*` | **V**: refg1 `fd/receipts-ref-g1/a1-read/readout.json` 4db170d3, refg1bars ba4b6985 |
| RSN: the weight-refit regressor moves the cells by at most 0.09σ | paper_body:122; supp:421 | `rsn-wr-sig-max` | **V**: rsn `fd/referee-sensitivity-20261111/connect-post/run-20261112/rsn_readout.json` 6291f48d |
| RSN: the common-phase-space C_model has 1.41 times the trace; the flags are unchanged | paper_body:165,408; supp:495 | `rsn-g6-trace`, `rsn-*` | **V**: rsn 6291f48d, rsnregrade cb5f5d17 |
| background template 2.91 % of data (2.72–3.23 % per playlist) | supp:46,668 | `bkg42-*` | **V**: lrows `methods-short-20261109/l-rows-20261112/derived/l_rows.json` dc3bf511 |
| background composition: about 10 % out-of-phase-space signal (1A); the rest mostly ν_μ CC with a true vertex outside the fiducial volume | supp:46 | `cbkg2-oops-1a`; text | **V**: cbkg2 `methods-short-20261109/cbkg2-20261112/members/cbkg2_summary.json` 22bb7782. The qualitative clause is not checked |
| the 16-cell result, its covariances, the per-group σ and the correlations | sec:cov16, tab:fived16-* | `f-*`, `sig*-*`, `corr-*`, `box-*` | **P**: 6 `sec-cov16_*.csv`, `tab-fived16-cells/-groups/-corr.csv` |
| validity classes, V-ATLAS (14 of 16 valid; R02 and R06 fail) | supp:validity | printed | **P**: `supp-validity.csv` (RP13; RP15/RP16 drop) |
| V-HALF | paper_body:241,354; supp:822 | `vhalf-*` | **V**: vhalf `valid-region-20261107/v-half/receipts/read/readout.json` e7423390. The package has `pending/V-HALF.txt` |
| generator comparisons | tab:gen16, tab:cmodel16, fig:ratio16 | `g-*` | **P**: `tab-gen16.csv`, `tab-cmodel16.csv`, `fig-ratio16.csv` |
| the 2D result and its four-block covariance | fig:validation, sec:uq2d | arrays | **P**: `fig-validation_result2d.csv`, the 6 `sec-uq2d_*.csv`, from the c2a transcription (S4) |

**No route** (the director's item 4):
- **N:** the LL5D five-observable coverage result. It is still pending at #977 a8713799.
- **L:** the five literals above, none checked by either builder:
  - Table 1's `T=382.8` and `138.5` at paper_body:232, duplicates of keyed values;
  - §6.1's 0.23 %, 0.37 % and 2.5 at paper_body:514.
- **Not in the package, V only:** the coverage, stability, RSN, background-composition, FD-PRR and
  algorithm-dependence claims. A depositee would need the repository and #977's value builder to reproduce them. The
  package, as it stands, has no file for any of them.

## Method and its limits

- The variants and keys were read with `tools/resolve_fv.py`. It keeps the `\fvcase` that `values_fived16.tex`
  selects, writes each `\fvval{key}` as `[[key=value]]` and strips LaTeX comments.
- `tools/log_checks.py` wraps the build's `Ctx.key/macro/printed` and calls `assemble()`, which only reads, to list
  every check: 895 rows, against the 985 the build counts. The difference is checks counted outside those three methods.
- **The key-to-readout mapping is by function:** a key's readout is one the assigning function reads. It is not traced
  per value.
- The quote checks inside `check_licences` are the re-pin list's domain (D3). They are not repeated here.
- Nothing was recomputed from physics inputs. No route here reruns the unfolding.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:**
- the clean-environment run of #981 at 91f9cb615: each command, its rc and its runtime;
- S1–S6 as findings for the re-pin;
- the claim map's routes at #977 a8713799.

**NOT CITABLE FOR:**
- any physics value;
- the correctness of any record;
- the deposit's contents or timing, which are Joseph's (D6);
- the claim map at any other #977 head;
- the sources of the L literals, which were not established here;
- Python 3.10 or 3.11, which were not measured.
  <!-- absence-ok: the scope of this record's own measurements (see S3) -->

Nothing is deposited, submitted or tagged.
