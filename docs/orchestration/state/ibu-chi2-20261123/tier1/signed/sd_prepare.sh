#!/bin/bash
# Login node, no Slurm. signed_data on the paper's pT edges: a fresh main clone (impl_e) with only signed_data.py's grid
# constants and ibukt/config.json's grid and input pins changed, and a stage of six pinned inputs. Writes under tier1/ only.
set -eo pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; T=$R/tier1; IMPL=$T/impl_e; ST=$T/stage_sd
MAIN=f00ed54b2d3489c8c0b7a705625e8a1c5820682d
for p in $IMPL $ST $T/sd_out; do [ ! -e $p ] || { echo "REFUSED: $p exists"; exit 2; }; done
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git $IMPL
git -C $IMPL -c advice.detachedHead=false checkout -q $MAIN
[ "$(git -C $IMPL rev-parse HEAD)" = $MAIN ] && [ "$(git -C $IMPL status --porcelain --ignored | wc -l)" = 0 ] || { echo "REFUSED: impl"; exit 2; }
python3 - $IMPL <<'PY'
import sys, json, pathlib
d = pathlib.Path(sys.argv[1]) / "2d-unfolding/ibukt"
s = (d / "signed_data.py").read_text()
for a, b in (('REFERENCE_DRIVER = "938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b"',
              'REFERENCE_DRIVER = "677ac75f1d171ca7d71223f62bf3426f056e41b1b6cc8bfd433d49528a1371e8"'),
             ('er_distance["chi2"], 465.41527219152636, rtol=1e-8', 'er_distance["chi2"], 434.8943632939891, rtol=1e-8'),
             ('zip(KS, (0.83, 1.03), strict=True)', 'zip(KS, (0.39, 0.54), strict=True)')):
    assert s.count(a) == 1, a; s = s.replace(a, b)
(d / "signed_data.py").write_text(s)
c = (d / "config.json").read_text()
for a, b in (('"a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"', '"5171c7b8ecacda6090e242349dd622218c1c38885c60ef8b91027033a8c4b780"'),
             ('"929d0e78011ead72e9677a05bad06eec80e914e181c8d02f94bbdea1c43b76f4"', '"b6cb61429b8d5a6f694147fb2ff985462eb433ab2478cda900d3ef8924ceaab0"')):
    assert c.count(a) == 1, a; c = c.replace(a, b)
j = json.loads(c); old = j["pt_edges"]; assert old == [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5], old
c = c.replace(json.dumps(old)[1:-1].replace(", ", ",\n    "), "X") if False else c
import re
m = re.search(r'"pt_edges": \[[^\]]*\]', c); assert m
new = m.group(0).replace("0.07,", "0.075,").replace("0.33,", "0.325,").replace("0.47,", "0.475,")
c = c[:m.start()] + new + c[m.end():]
assert json.loads(c)["pt_edges"] == [0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5]
(d / "config.json").write_text(c)
PY
mkdir -p $ST
cp $T/stage/runEventLoopOmniFold_MEFHC.root $ST/cv.root; cp $T/stage/runEventLoopMC_MEFHC.root $ST/flux.root
cp $T/units_e/er.root $ST/er.root; cp $T/units_e/c2_central.npz $ST/c2.npz
dd if=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root of=$ST/paper.root iflag=noatime status=none
dd if=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so of=$ST/libRooUnfold.so iflag=noatime status=none
chmod a-w $ST/*
sha256sum $ST/*
git -C $IMPL diff > $T/impl_e.diff; git -C $IMPL diff --stat; sha256sum $T/impl_e.diff $IMPL/2d-unfolding/ibukt/signed_data.py $IMPL/2d-unfolding/ibukt/config.json
python3 -c "import json; c=json.load(open('$IMPL/2d-unfolding/ibukt/config.json')); print('library pin', c['inputs']['library'])"
