# RSN's HPSS archive kit (2026-11-11), for the director's go

**By** session tier3-design, at the director's ruling on RSN rev 2: "archive now, the ~25 MB: pv-ladder prep/,
products/ and cpl_block.npz", under hpss-20261111's discipline (#1054). **Nothing has run on NERSC.** It runs only once
NERSC is reachable, Joseph has renewed his certificate and the director has given the go for these exact sha256s.

| file | sha256 | role |
|---|---|---|
| `hpss_rsn.sh` | `877d9840a182a5e215d66903ca23b157dcc4872526bf67b30aa1963e35a43c9f` | the archive script: the template with its list embedded (what runs) |
| `hpss_rsn_launch.sh` | `9b29f0d4ae9e31ea74f48ccc3b69a805a467145506e4be34766883d4be2c8794` | the Mac-side launcher: archive and fetch modes, to a dtnNN node |
| `hpss_rsn.template.sh` | `da7c418dc76cb95eb3ae031b8ac5465c8dd9157c39441364ef5848b96e5940a9` | the template; `make_hpss_script.py` fills in `LIST_SHA` and appends the list |
| `hpss_rsn_list.tsv` | `0dafaac8e3664875f496974fb79f73e319ada7647eb5106dbe6626cefa9d99c6` | 67 rows, group<TAB>sha256<TAB>path |
| `make_hpss_script.py` | `d2f2a43a…` | byte-identical to hpss-20261111's `connect/make_hpss_script.py` |
| `smoke.txt` | — | the local smoke run (below) |

**What it archives.** 67 files, every one an explicit path with its committed sha256 pin:
- **pvl_prep:** pv-ladder's `prep/`, 36 files, pinned by `nd-unfolding/pv-ladder/prep-SHA256SUMS`;
- **pvl_products:** pv-ladder's `products/`, 30 files, pinned by the `products/` rows of
  `state/measurement-scoping/pv-ladder/receipts/SHA256SUMS`;
- **cpl_block:** `fd-ct-5b-addition-20261031/with/block/cpl_block.npz`, pinned by F0b's `--extra-block-sha256`
  `d9aa32fd…`.

The target is `/home/j/josephrb/mnv-rsn-inputs-20261111/`, one `<group>.tar` per group. The output goes to
`/pscratch/sd/j/josephrb/hpss-rsn-20261111/` (logs, manifests, `stat.<group>.tsv`).

**The discipline, as #1054's.**
- Every source is read once by `os.open(O_RDONLY | O_NOATIME)` into `/dev/shm`, so htar never reads pscratch. The
  sources' atimes, and so their purge clocks, do not move.
- Size, mtime and atime must be unchanged by the copy, and the bytes read must equal the size.
- htar runs with `-Hcrc -Hverify=1`, followed by `hsi hashcreate` and `hashverify`.
- Before anything runs, the quota preflight must pass, and the HPSS target must not exist, so nothing is overwritten.
- Any failure is a STOP (exit 8). Nothing is repaired or deleted.

**Five changes, each marked `[RSN]` in the template:**
1. It refuses unless the host is a data-transfer node (`dtnNN`) and no Slurm job is set.
2. Each file's sha256 must equal its committed pin, which is stronger than #1054's size and mtime check against a
   stat list. Size and mtime are recorded beside the manifest.
3. **Every member is re-read from HPSS:** `htar -xf` of the whole tar into `/dev/shm`, and each retrieved file's
   sha256 must equal its manifest line and its pin. #1054 retrieved only each group's smallest file.
4. It has no squeue fence. A data-transfer node is not a Slurm client, and the sources are only read, by O_NOATIME,
   never written. The director's go is the fence.
5. The /dev/shm headroom is twice the group's bytes plus 256 MiB.

**The smoke run (local, `smoke.txt`).** It used stubs for `hsi`, `htar`, `hpssquota` and `timeout`, and synthetic
sources with real sha256 pins. macOS has no O_NOATIME, so the first case ran without it: its read moved atime, and
the script STOPped at the atime guard, as it must. The other cases neutralized only that comparison.

| case | result |
|---|---|
| a read that moves atime | STAGE STOP at the first file |
| the pass path | `ARCHIVE PASS`; three tars; every member re-read and equal to its pin |
| a wrong pin in the second group | STAGE STOP there; the first group's tar stays and is reported |
| one byte corrupted on retrieval | RETRIEVE STOP ("1 differing") |
| an existing HPSS target | STOP before any group |
| a row count other than declared | STOP |
| a login host, or a Slurm job set | refused before any log (rc 9) |

**To run (the cluster lane, after the go):**
`bash hpss_rsn_launch.sh archive <new empty dir> dtnNN`, then `bash hpss_rsn_launch.sh fetch <new empty dir> dtnNN`.
Commit the fetched logs, manifests and `stat.*.tsv` as the receipt.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the kit and its local smoke behaviour.
- **Not citable for:** any archive having been made.
