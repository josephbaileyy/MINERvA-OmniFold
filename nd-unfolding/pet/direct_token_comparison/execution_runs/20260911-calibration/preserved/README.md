# Recover the original failed-allocation payload

`payload.tar.gz` contains the 13 original closed files under `payload/`, totaling
51,619 uncompressed bytes. Every file was read back from the archive and matched
to `preservation.json`, independently of the CFS verification. The raw guard
receipt is unchanged; the adjacent execution revision binding identifies its
historical driver at `106ba9a8` rather than pinning the corrected working tree.

Extract into a new empty directory:

```bash
mkdir recovered-calibration-58198332
tar -xzf payload.tar.gz -C recovered-calibration-58198332
```

The original accounting is `payload/accounting.txt`; failure output and guard
records are under `payload/calibration/`. `preservation.json` lists every file,
size and SHA-256 and gives the independently verified CFS source/destination.
No scientific model, weight or prediction artifacts were produced.
