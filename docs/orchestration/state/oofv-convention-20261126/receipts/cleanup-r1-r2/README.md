# Removal of the superseded OOFVC scratch roots (attempt 1 and r2)

Joseph approved it on 2026-11-27, relayed by the director: "you can remove things that are unused". The director gave
the GOs: first the manifest connect, then the remove connect naming the manifest's LISTING_SHA. cov2d acked each
connect (04:44:46Z, 04:59:20Z). Both ran after r3's post and fetch.

## The package

The package is `2d-unfolding/oofvc/launch/cleanup/`:
- `oofvc_cleanup.sh`, sha256 `0a6b59ec3b33990c4a351fcf4ae2dd0e9cc7e0307fd22562738a8619b3270a65`, runs on the node;
- `oofvc_cleanup_launch.sh`, sha256 `6c71deb1bd8e073e62d9d88ff290e5b76a3d2c5e92175fd3d2b2c065d18998c6`, runs on the Mac
  and stages the script in /dev/shm with a sha check.

The director accepted both before either ran. The script's gates all fail closed:
- the user is josephrb;
- squeue succeeds and lists no `oofvc_` job;
- each root passes lstat: it is not a symlink, it is a directory I own, its `readlink -f` is itself, and r3 is not
  under it;
- no name contains a newline or tab;
- `find -xdev` sees every entry;
- no regular file has more than one hard link;
- r3's listing sha is recorded before and after.

`remove` refuses unless the recomputed listing equals the manifested sha. It then runs `rm -rf --one-file-system --` on
each literal root and checks that the root is absent. `harness.sh.txt` ran the script byte-identical in
`debian:bookworm-slim` on fake trees: 17/17 cases pass (`harness-out.txt`). The one gate not exercised is the
filesystem-crossing gate, since the container has no second mount.

## Results

| connect | file | result |
|---|---|---|
| manifest (04:45:06–04:58:38Z) | `manifest-launcher.txt`, `manifest-session.txt.gz` (the full session.out, gzip -n) | 92,582 entries: oofvc-20261126 has 35,292 (1,750,767,300 B, listing `8e23b939…`) and oofvc-20261126-r2 has 57,290 (6,940,841,849 B, listing `b9d87081…`). LISTING_SHA is `0d88dfb3ad567fec65addfb8ac90e0c942c434b13162c072351a0a174942c191`. There are 83,051 files, 8,928 dirs and 603 symlinks, all relative (inside the git clones). One file was unhashed (≥ 1e9 B): r2/stage/runEventLoopOmniFold_MEFHC.root, 2,144,008,221 B, the staged copy of 43f8cc16. r3's listing was unchanged (`04aa5afb…`) |
| remove (04:59:36–05:00:53Z) | `remove-launcher.txt` | The listing matched 0d88dfb3…. Both roots were removed (rm rc 0), and each was confirmed gone. r3's listing after is `04aa5afb…`, unchanged |
| independent check (05:01:08Z) | `confirm-gone.txt` | Both old roots are absent, and r3 is present |

The uncompressed manifest's sha256 is `886bfe4372665b54cbd5dfc37b45e3f312f44e0876867fc6512b6348dafb75f5` (92,593
lines).
