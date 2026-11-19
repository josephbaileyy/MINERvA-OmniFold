#!/usr/bin/env python3
"""The composed Figs. 7 (projections), 9 and 10 hold their installed items unchanged, plus only what compose_tier2.py
adds.

usage: python3 -I check_tier2.py <composed capture dir> <palette pass runs dir (note-figstyle-20261117/runs)>

Each capture is fig-restyle-20261031/tools/artists.py's index (capture_palette.py): per item a full hash (data,
colours, styles) and an "xhash" (data alone, colours and line styles left out). The installed files' captures are
the palette pass's committed arm-1 captures: xsec_proj/ (Fig. 7's projections), paper_slices/ (Figs. 9 and 10) and
models/ (Fig. 13).
- **Projections:** the composed items must be the installed projection's items plus two more. One is Fig. 13's
  published line, with an equal full hash. The other is Fig. 13's Tune v1 line, with an equal xhash (it is restyled
  dashed).
- **Slices:** every installed item must be present with an equal full hash. Each extra item must be drawn in the
  published points' black. There must be at least one extra item per panel.
  compose_tier2.py's report holds the numeric checks of those values: the ratio to the mosaic, and the prior.
Prints one line per figure, then CHECK-TIER2 :: PASS or FAIL.
"""
import json
import sys
from collections import Counter
from pathlib import Path


def items(p):
    d = json.loads(Path(p).read_text())
    return d["items"] if isinstance(d, dict) and "items" in d else d


new, runs = Path(sys.argv[1]), Path(sys.argv[2])
ok = True
mc = items(runs / "models/arm1/capture/models/model_comp_projections.pdf.json")
for k, stem in enumerate(("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")):
    a = items(new / f"{stem}.pdf.json")
    b = items(runs / f"xsec_proj/arm1/capture/xsec_proj/{stem}.pdf.json")
    src = [it for it in mc if it["axes"] == k]
    pub = [it for it in src if it["label"].startswith("Published")]
    tune = [it for it in src if it["label"].startswith("GENIE")]
    extra = Counter(it["hash"] for it in a) - Counter(it["hash"] for it in b)
    missing = Counter(it["hash"] for it in b) - Counter(it["hash"] for it in a)
    left = [it for it in a if it["hash"] in extra]
    good = (not missing and len(pub) == 1 and len(tune) == 1 and len(left) == 2
            and sum(it["hash"] == pub[0]["hash"] for it in left) == 1
            and sum(it["xhash"] == tune[0]["xhash"] for it in left) == 1)
    print(f"{stem}: {len(a)} items = installed {len(b)} + {len(left)} added (published hash equal: "
          f"{any(it['hash'] == pub[0]['hash'] for it in left)}; Tune v1 published-prediction xhash equal: "
          f"{any(it['xhash'] == tune[0]['xhash'] for it in left)}); installed items missing: {sum(missing.values())}")
    ok &= good
for stem in ("MEFHC_5iter_xsec_paper_pt_slices", "MEFHC_5iter_xsec_paper_pz_slices"):
    a = items(new / f"{stem}.pdf.json")
    b = items(runs / f"paper_slices/arm1/capture/paper_slices/{stem}.pdf.json")
    missing = Counter(it["hash"] for it in b) - Counter(it["hash"] for it in a)
    extra = Counter(it["hash"] for it in a) - Counter(it["hash"] for it in b)
    left = [it for it in a if it["hash"] in extra]
    black = [it for it in left if all(c.upper().startswith("#000000") for v in it.get("colours", {}).values()
                                      if isinstance(v, list) for c in v)]   # "cmap" is a name, not a colour
    panels = {it["axes"] for it in left}
    npan = len({it["axes"] for it in b})
    good = not missing and left and len(black) == len(left) and len(panels) >= npan - 1
    print(f"{stem}: {len(a)} items = installed {len(b)} + {len(left)} added (all black: {len(black) == len(left)}; "
          f"in {len(panels)} axes); installed items missing: {sum(missing.values())}")
    ok &= bool(good)
print(f"CHECK-TIER2 :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
