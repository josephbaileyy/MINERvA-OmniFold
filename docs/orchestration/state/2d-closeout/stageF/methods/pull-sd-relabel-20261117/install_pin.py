#!/usr/bin/env python3
"""The installer pin of the relabelled note figure (README.md section 5), after the run, its record and check_sd.py PASS.

usage: python3 -I install_pin.py <repo root>
Reads the run's record, committed under this package's run/ (run/SHA256SUMS: the connect's listing of every arm file),
and edits the tree in place, each edit an exact substitution asserted once:
  1. figs/MEFHC_5iter_pull_full.pdf: a copy of run/after/out/MEFHC_5iter_pull_full.pdf, which must have the digest
     run/SHA256SUMS lists for after/out/MEFHC_5iter_pull_full.pdf; figs/SHA256SUMS lists it.
  2. docs/analysis-note/figures/MEFHC_5iter_pull_full.pdf: the same copy (the installed figure).
  3. docs/analysis-note/make_figures.sh: the fig-restyle install line of MEFHC_5iter_pull_full.pdf (fd84d992) becomes a
     comment, and after the restyle block's last install line, RSG names this package's figs/ and install_restyle_fig
     installs the new digest from it (check_ledger.py requires "install_restyle_fig <basename> <sha256>" and reads the
     copy from the G row's copy directory).
  4. re2-integration/ledger.tsv: the G row FIG-MEFHC_5iter_pull_full is re-pointed (ruling 1 of fig-restyle-20261031:
     re-point, do not replace): the new digest, run/SHA256SUMS and its entry, and figs/ as the copy directory.
  5. DIGESTS.tsv: the figure's old digest (fig-restyle-20261031/run-a2/after/SHA256SUMS) and new one.
Prints each digest and file written."""
import hashlib
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1]).resolve()
M = "docs/orchestration/state/2d-closeout/stageF/methods"
PS = f"{M}/pull-sd-relabel-20261117"
BASE = "MEFHC_5iter_pull_full.pdf"
ENTRY = f"after/out/{BASE}"
OLD = "fd84d992f3b212be3be6da06badbe3dfb5123f160f34f10e81d7f65cc80afd3d"
OLD_SUMS = f"{M}/fig-restyle-20261031/run-a2/after/SHA256SUMS"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sub(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)


run = R / PS / "run"
listed = [ln.split()[0] for ln in (run / "SHA256SUMS").read_text().splitlines() if ln.split()[1:] == [ENTRY]]
assert len(listed) == 1, listed
new = listed[0]
assert sha(run / ENTRY) == new, "the run's after PDF is not its SHA256SUMS digest"
assert new != OLD
old_listed = [ln.split()[0] for ln in (R / OLD_SUMS).read_text().splitlines() if ln.split()[1:] == [f"out/{BASE}"]]
assert old_listed == [OLD], old_listed
# every edit is made in memory and checked before any file is written
mk = R / "docs/analysis-note/make_figures.sh"
mk_text = sub(mk.read_text(), f"install_restyle_fig {BASE}             {OLD}\n",
              f"# install_restyle_fig {BASE}           {OLD}\n")
last = ("install_restyle_fig model_comp_ratio_maps.pdf             "
        "838e5fc4669cf4d58b20f81dbda29f5131c1a57a9d34202948b9830ab51648bd\n")
mk_text = sub(mk_text, last, last + (
    "# 2026-11-17: MEFHC_5iter_pull_full.pdf prints the spread of its standardized differences as \"SD\", their standard\n"
    "# deviation (numpy.std), not \"rms\" (DECISION-20261116-joseph-paper-batch.md item 16; pull-sd-relabel-20261117/\n"
    "# README.md). It is installed from that package's figs/, the \"after\" arm of its login-node run (run/SHA256SUMS),\n"
    "# whose data artists are run-a2's bit for bit (check_sd.py K3); its fig-restyle line above stays as a comment.\n"
    f"RSG=\"$REPO/{PS}/figs\"\n"
    f"install_restyle_fig {BASE}             {new}\n"))
led = R / M / "re2-integration/ledger.tsv"
row = [ln for ln in led.read_text().splitlines() if ln.startswith("G\tFIG-MEFHC_5iter_pull_full\t")]
assert len(row) == 1 and row[0].split("\t")[3] == OLD, row
led_text = sub(led.read_text(), row[0] + "\n", "\t".join(["G", "FIG-MEFHC_5iter_pull_full", BASE, new,
                                                          f"{PS}/run/SHA256SUMS", ENTRY, f"{PS}/figs"]) + "\n")
figs = R / PS / "figs"
figs.mkdir(exist_ok=True)
for dst in (figs / BASE, R / "docs/analysis-note/figures" / BASE):
    shutil.copyfile(run / ENTRY, dst)
    assert sha(dst) == new
    print(f"wrote {dst.relative_to(R)} {new}")
(figs / "SHA256SUMS").write_text(f"{new}  {BASE}\n")
mk.write_text(mk_text)
led.write_text(led_text)
print(f"edited {mk.relative_to(R)} and {led.relative_to(R)}")
(R / PS / "DIGESTS.tsv").write_text(
    "basename\told_sha256\told_SHA256SUMS\told_entry\tnew_sha256\tnew_SHA256SUMS\tnew_entry\n"
    f"{BASE}\t{OLD}\t{OLD_SUMS}\tout/{BASE}\t{new}\t{PS}/run/SHA256SUMS\t{ENTRY}\n")
print(f"wrote {PS}/DIGESTS.tsv; {BASE}: {OLD[:12]} -> {new[:12]}")
