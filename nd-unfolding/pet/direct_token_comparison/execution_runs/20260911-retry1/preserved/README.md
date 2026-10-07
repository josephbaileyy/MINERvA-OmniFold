# Recover the original retry payload

`payload.tar.gz` preserves all 19 closed files under `payload/`, totaling
511,304 bytes. Source, CFS, local raw copy and archive readback were compared
file-by-file with `preservation.json`. The raw guard receipts are unchanged;
the adjacent execution revision binding refers to commit `46fe3d7c`.

Extract into a new empty directory:

```bash
mkdir recovered-calibration-58201775
tar -xzf payload.tar.gz -C recovered-calibration-58201775
```

`payload/accounting.txt` contains both attempts. Partial pooled models and
predictions are under `payload/calibration/measurement/`. They are calibration
artifacts, excluded from the full matrix; there is no complete paired result.
